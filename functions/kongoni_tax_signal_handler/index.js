'use strict';

const { handleSignal } = require('./src/handler');

module.exports = async (event, context) => {
  try {
    const result = await handleSignal(event.getRawData());
    console.log(JSON.stringify({
      message: 'Tax Signal events processed.',
      processed: result.processed,
      results: result.results
    }));
    context.closeWithSuccess();
  } catch (error) {
    console.error(JSON.stringify({
      message: 'Tax Signal processing failed.',
      error: error.message
    }));
    context.closeWithFailure();
  }
};
