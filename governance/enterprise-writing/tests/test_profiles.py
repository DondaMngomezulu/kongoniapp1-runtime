import copy
import json
import pathlib
import unittest
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = pathlib.Path(__file__).resolve().parents[1]
def load(path): return json.loads((ROOT / path).read_text())
class ProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping = load('manifest/discipline-profile-mapping.json')
        cls.common = load('schemas/common/document-envelope.schema.json')
        cls.registry = Registry().with_resource(cls.common['$id'], Resource.from_contents(cls.common))
    @staticmethod
    def specimen(prop):
        if prop.get('type') == 'string': return 'Sample reference'
        if prop.get('type') == 'array':
            item = prop['items']
            if item.get('type') == 'string': return ['Sample item']
            if item.get('type') == 'object': return [{'id':'E1','summary':'Synthetic entry'}]
        raise ValueError(prop)
    def sample(self, record, schema):
        props = schema['properties']['content']['properties']
        required = schema['properties']['content']['required']
        return {'metadata': {'document_id':'TEST-'+record['profile_key'], 'document_title':'Synthetic validation case',
            'discipline_key':record['discipline_key'],'profile_key':record['profile_key'],
            'profile_version':'1.0.0-draft','lifecycle_status':'DRAFT',
            'document_type_binding':{'status':'PENDING'},'source_references':[]},
            'content':{k:self.specimen(props[k]) for k in required}}
    def test_18_unique_profiles(self):
        records=self.mapping['profiles']
        self.assertEqual(len(records),18)
        for key in ('discipline_key','profile_key','candidate_schema_id','schema_path'):
            self.assertEqual(len({r[key] for r in records}),18)
    def test_profiles_positive_negative(self):
        for record in self.mapping['profiles']:
            with self.subTest(profile=record['profile_key']):
                schema=load(record['schema_path'])
                Draft202012Validator.check_schema(schema)
                self.assertEqual(record['candidate_schema_id'],schema['$id'])
                validator=Draft202012Validator(schema,registry=self.registry)
                sample=self.sample(record,schema)
                self.assertTrue(validator.is_valid(sample),list(validator.iter_errors(sample)))
                bad=copy.deepcopy(sample);bad['metadata']['discipline_key']='wrong-discipline'
                self.assertFalse(validator.is_valid(bad))
                bad=copy.deepcopy(sample);bad['metadata']['profile_key']='ew.wrong.v1'
                self.assertFalse(validator.is_valid(bad))
                bad=copy.deepcopy(sample);bad['content'].pop(next(iter(schema['properties']['content']['required'])))
                self.assertFalse(validator.is_valid(bad))
                bad=copy.deepcopy(sample);bad['metadata']['document_type_binding']={'status':'MAPPED'}
                self.assertFalse(validator.is_valid(bad))
                bad=copy.deepcopy(sample);bad['content']['unregistered_field']='not allowed'
                self.assertFalse(validator.is_valid(bad))
    def test_shared_envelope(self):
        Draft202012Validator.check_schema(self.common)
        self.assertEqual(self.mapping['shared_envelope'],self.common['$id'])
    def test_conformance_gates(self):
        for r in self.mapping['profiles']:
            self.assertEqual('NOT_TESTED',r['native_conformance'])
            self.assertEqual('NOT_VERIFIED',r['semantic_alignment'])
if __name__ == '__main__': unittest.main()
