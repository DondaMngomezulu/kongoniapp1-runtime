/**
 * Health probe for the Kongoniapp1 runtime.
 *
 * Basic I/O function. Confirms that the deployed runtime is reachable and
 * reports which build of the repository is serving the request.
 *
 * Kept dependency-free on purpose: it must stay up even when application
 * dependencies are broken. Functions that need Catalyst services should add
 * "zcatalyst-sdk-node" to their own package.json.
 *
 * @param {object} context Catalyst execution context
 * @param {object} basicIO Catalyst basic I/O handle
 */
module.exports = (context, basicIO) => {
	basicIO.write(
		JSON.stringify({
			status: 'ok',
			service: 'kongoniapp1-runtime',
			function: 'kongoniapp1_health'
		})
	);

	context.close();
};
