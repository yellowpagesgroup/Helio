(function() {
	'use strict';

    var url, page, timeout,
		args = require('system').args;

	// arg[0]: scriptName, args[1...]: arguments
	if (args.length < 2 || args.length > 3) {
		console.error('Usage:\n  phantomjs runner.js [url-of-your-qunit-testsuite] [timeout-in-seconds]');
		phantom.exit(1);
	}

	url = args[1];
	page = require('webpage').create();
	if (args[2] !== undefined) {
		timeout = parseInt(args[2], 10);
	}

    page.onInitialized = function() {
        page.evaluate(addLogging);
	};

    page.onConsoleMessage = function (msg) {
        console.log(msg);
    };

    page.onCallback = function(message) {
		var result,
			failed;

		if (message) {
			if (message.name === 'Jasmine.done') {
				failed = message.failed;

				phantom.exit(failed ? 1 : 0);
			}
		}
	};

	page.open(url, function(status) {
		if (status !== 'success') {
			console.error('Unable to access network: ' + status);
			phantom.exit(1);
		} else {
			// Cannot do this verification with the 'DOMContentLoaded' handler because it
			// will be too late to attach it if a page does not have any script tags.

			// Set a timeout on the test running, otherwise tests with async problems will hang forever
			if (typeof timeout === 'number') {
				setTimeout(function() {
					console.error('The specified timeout of ' + timeout + ' seconds has expired. Aborting...');
					phantom.exit(1);
				}, timeout * 1000);
			}
		}
	});

    function addLogging() {
        window.document.addEventListener('DOMContentLoaded', function() {
            var jasmineComplete = function(failed){ // implement this with built in jasmine finishCallback property
                if (typeof window.callPhantom === 'function') {
					window.callPhantom({
						'name': 'Jasmine.done',
                        'failed': failed
					});
				}
            }

            jasmine.getEnv().addReporter(new jasmine.ConsoleReporter(jasmineComplete));
            jasmine.getEnv().execute();
        });
    }
})();