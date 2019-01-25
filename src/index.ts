// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.

// import * as libembed from './libembed';
declare var  __webpack_public_path__:string;
// needed to make fontawesome work
__webpack_public_path__ = 'resources/'

import {Manager} from './manager';
import 'font-awesome/css/font-awesome.css';
import '@phosphor/widgets/style/index.css';
import '@jupyter-widgets/controls/css/widgets.built.css';
/**
 * Render widgets in a given element.
 *
 * @param element (default document.documentElement) The element containing widget state and views.
 * @param loader (default requireLoader) The function used to look up the modules containing
 * the widgets' models and views classes. (The default loader looks them up on unpkg.com)
 */
// export
// function renderWidgets(element = document.documentElement, loader: (moduleName: string, moduleVersion: string) => Promise<any>  = requireLoader) {
//     requirePromise(['@jupyter-widgets/html-manager']).then((htmlmanager) => {
//         let managerFactory = () => {
//             return new htmlmanager.HTMLManager({loader: loader});
//         }
//         libembed.renderWidgets(managerFactory, element);
//     });
// }

export
function renderWidgets() {
    console.log('rendering widgets')
    let manager = new Manager();
    manager.load();

}

// (window as any).require(['@jupyter-widgets/html-manager/dist/libembed-amd'], function(embed) {
// if (document.readyState === "complete") {
//     renderWidgets();
// } else {
//     window.addEventListener('load', function() {renderWidgets();});
// }
// });

