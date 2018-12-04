

let cdn = 'https://unpkg.com/';

// find the data-cdn for any script tag, assuming it is only used for embed-amd.js
const scripts = document.getElementsByTagName('script');
Array.prototype.forEach.call(scripts, (script) => {
    cdn = script.getAttribute('data-jupyter-widgets-cdn') || cdn;
});

/**
 * Load a package using requirejs and return a promise
 *
 * @param pkg Package name or names to load
 */
let requirePromise = function(pkg: string | string[]): Promise<any> {
    return new Promise((resolve, reject) => {
        let require = (window as any).requirejs;
        if (require === undefined) {
            reject("Requirejs is needed, please ensure it is loaded on the page.");
        } else {
            require(pkg, resolve, reject);
        }
    });
}

function moduleNameToCDNUrl(moduleName: string, moduleVersion: string) {
    let packageName = moduleName;
    let fileName = 'index'; // default filename
    // if a '/' is present, like 'foo/bar', packageName is changed to 'foo', and path to 'bar'
    // We first find the first '/'
    let index = moduleName.indexOf('/');
    if ((index != -1) && (moduleName[0] == '@')) {
        // if we have a namespace, it's a different story
        // @foo/bar/baz should translate to @foo/bar and baz
        // so we find the 2nd '/'
        index = moduleName.indexOf('/', index+1);
    }
    if (index != -1) {
        fileName = moduleName.substr(index+1);
        packageName = moduleName.substr(0, index);
    }
    return `${cdn}${packageName}@${moduleVersion}/dist/${fileName}`;
}

export
function requireLoader(moduleName: string, moduleVersion: string) {
    return requirePromise([`${moduleName}`]).catch((err) => {
        let failedId = err.requireModules && err.requireModules[0];
        if (failedId) {
            console.log(`Falling back to ${cdn} for ${moduleName}@${moduleVersion}`);
            let require = (window as any).requirejs;
            if (require === undefined) {
                throw new Error("Requirejs is needed, please ensure it is loaded on the page.");
            }
            const conf = {paths: {}};
            conf.paths[moduleName] = moduleNameToCDNUrl(moduleName, moduleVersion);
            require.undef(failedId);
            require.config(conf);

            return requirePromise([`${moduleName}`]);
       }
    });
}
