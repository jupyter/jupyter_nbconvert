
import * as base from '@jupyter-widgets/base'
import * as controls from '@jupyter-widgets/controls';
import * as pWidget from '@phosphor/widgets';
import { Signal } from '@phosphor/signaling';

import { HTMLManager } from '@jupyter-widgets/html-manager';

import * as outputWidgets from './output';
import {requireLoader as loader} from './loader'
import { ShimmedComm } from './services-shim';
import { createRenderMimeRegistryWithWidgets } from './renderMime';

import * as domtoimage from 'dom-to-image';
import * as html2canvas from 'html2canvas'

// let (window as any)
if (typeof window !== "undefined" && typeof (window as any).define !== "undefined") {
  (window as any).define("@jupyter-widgets/base", base);
  (window as any).define("@jupyter-widgets/controls", controls);
}

let viewIdSnapshots = {}

// http://lea.verou.me/2016/12/resolve-promises-externally-with-this-one-weird-trick/
class defer {
    constructor() {
        this.promise = new Promise((resolve, reject) => {
            this.res = resolve;
            this.rej = reject;
        });
    }


    promise: any;
    rej: any;
    res: any;
}

async function getViewSnapshot(viewId) {
    if(viewIdSnapshots[viewId] === undefined) {
        viewIdSnapshots[viewId] = new defer();
    } else{
        return viewIdSnapshots[viewId]
    }
}

export class Manager extends HTMLManager {
    constructor() {
        console.log('manager')
        super({loader: loader});

        // for (let i=0; i!=tags.length; ++i) {
        //     renderManager(element, JSON.parse(tags[i].innerHTML), managerFactory);
        // }        
        // this.kernel = kernel;
        // this.registerWithKernel(kernel)
        // this.loader = loader;
        // this.renderMime = createRenderMimeRegistryWithWidgets(this);
        // this._onError = new Signal(this)
        // this.build_widgets()
    }
    async load() {
        let htmlElements = document.body.querySelectorAll('div.output_html');
        htmlElements.forEach((el) => {
            setTimeout(() => {
                html2canvas(el, {useCORS: true}).then(canvas => {
                // document.body.appendChild(canvas)
                    el.appendChild(canvas)
                    let imageData = canvas.toDataURL('image/png');
                    let cell_index = Number(el.getAttribute('data-nb-cell-index'));
                    let output_index = Number(el.getAttribute('data-nb-output-index'));
                    var xmlHttp = new XMLHttpRequest();
                    xmlHttp.open("post", "/send_snapshot"); 
                    xmlHttp.send(JSON.stringify({cell_index: cell_index, output_index: output_index, image_data: imageData}));
                });
            }, 1000);

        })

        let tags = document.body.querySelectorAll('script[type="application/vnd.jupyter.widget-state+json"]');
        if(tags.length == 0) {
            console.error('no state found')
        } else if(tags.length > 1) {
            console.error('no state found')
        } else {
            let state = JSON.parse(tags[0].innerHTML);
            let models = await this.set_state(state);
            this.models = models;
            let viewTags = document.body.querySelectorAll('script[type="application/vnd.jupyter.widget-view+json"]');
            let views = [];
            for (let i=0; i!=viewTags.length; ++i) {
                let viewtag = viewTags[i];
                let widgetViewObject = JSON.parse(viewtag.innerHTML);
                let model_id: string = widgetViewObject.model_id;
                let model = models.filter( (item) => {
                    return item.model_id == model_id;
                })[0];
                if (model !== undefined) {
                    let prev = viewtag.previousElementSibling;
                    if (prev && prev.tagName === 'img' && prev.classList.contains('jupyter-widget')) {
                        viewtag.parentElement.removeChild(prev);
                    }
                    let widgetTag = document.createElement('div');
                    widgetTag.className = 'widget-subarea';
                    viewtag.parentElement.insertBefore(widgetTag, viewtag);
                    let options = { el : widgetTag };
                    // await this.display_model(undefined, model, { el : widgetTag });
                    let view = await this.create_view(model, options) ;//.then(
                    views.push(view);
                    this.display_view(undefined, view, options);//.catch(utils.reject('Could not create view', true));
                }
            }
            let all_view_promises = [];
            models.forEach((model) => {
                for(let id in model.views) {
                    all_view_promises.push(model.views[id])
                }
            })
            console.log('views', all_view_promises);
            let all_views = await Promise.all(all_view_promises);
            let bqplot_figure_views = all_views.filter((view) => view.model.name == 'FigureModel');
            console.log('bqplot_figure_views', bqplot_figure_views);
            await Promise.all(bqplot_figure_views.map(async (view) => {
                while(!view.mark_views) {
                    await new Promise((resolve) => setTimeout(resolve, 100));
                }
                let marks = await Promise.all(view.mark_views.views);
                await new Promise((resolve) => {
                    setTimeout(async () => {
                        // this is code from bqplot, make bqplot such that we can rely on a method
                        // of figure
                        var xml = view.get_svg();
                        // Render a SVG data into a canvas and download as PNG.
                        var image = new Image();
                        var that = this;
                        let image_loaded_promise = new Promise((resolve) => image.onload=resolve);
                        image.src = "data:image/svg+xml;base64," + btoa(xml);
                        await image_loaded_promise;
                        var canvas = document.createElement("canvas");
                        canvas.classList.add('bqplot');
                        canvas.width = view.width * window.devicePixelRatio;;
                        canvas.height = view.height * window.devicePixelRatio;
                        canvas.style.width = view.width;
                        canvas.style.height = view.height;
                        canvas.getContext('2d').scale(window.devicePixelRatio, window.devicePixelRatio);
                        var context = canvas.getContext("2d");
                        context.drawImage(image, 0, 0);
                        view.el.parentElement.replaceChild(canvas, view.el)
                        view.el = canvas; // dirty, but then html2canvas can find it
                        console.log('bqplot figure replaced by snapshot')
                        resolve()
                    }, 1000);
                });
            }));
            /*await views.map((view) => {
                    return new Promise(async (resolve_view) => {
                        // convert bqplot figures by a static png before we do the html2canvas
                        if(view.model.name == 'FigureModel') {
                            console.log(view)
                            // TODO: change bqplot such that we have a promise to wait for
                            // instead of polling it
                            resolve_view();
                        } else {
                            // await Promise.resolve(1);
                            resolve_view();
                            await Promise.resolve(1);
                        }
                    });
                }))
            })*/
            console.log('All views converted')
            views.forEach(async (view) => {
                let callbacks = (window as any)._webgl_update_callbacks;
                console.log('callbacks', callbacks)
                if(callbacks) {
                    callbacks.forEach((callback) => callback())
                }
                // let dependencies = [];
                if(view.model.name == 'LeafletMapModel') {
                    // TODO: change jupyter-leaflet such that we have a promise to wait for
                    // instead of polling it
                    while(!view.obj) {
                        await new Promise((resolve) => setTimeout(resolve, 100));
                    }
                    for(var i=0; i < view.layer_views.views.length; i++) {
                        let layer = await view.layer_views.views[i];
                        // wait for max 10 seconds
                        let timeout = new Promise((resolve) => {setTimeout(() => {console.log('timeout'); resolve()}, 10*1000)});
                        let loaded = new Promise((resolve) => {console.log('loaded'); layer.obj.on('load', resolve)})
                        layer.obj.on('load', () => console.log('loaded!!'))
                        await Promise.race([timeout, loaded]);
                        console.log('done')

                    }
                }
                setTimeout(() => {
                    console.log('make screenshot')
                    html2canvas(view.el, {useCORS: true}).then(canvas => {
                    // document.body.appendChild(canvas)
                        view.el.parentElement.appendChild(canvas)
                        let imageData = canvas.toDataURL('image/png');
                        let outputElement = view.el.parentElement.parentElement;''
                        let cell_index = Number(outputElement.getAttribute('data-nb-cell-index'));
                        let output_index = Number(outputElement.getAttribute('data-nb-output-index'));
                        var xmlHttp = new XMLHttpRequest();
                        xmlHttp.open("post", "/send_snapshot"); 
                        xmlHttp.send(JSON.stringify({cell_index: cell_index, output_index: output_index, image_data: imageData}));
                    });
                }, 1000);
            })


        }

    }
    _display_view(msg, view, options) {
        console.log(msg, view, options)
        let result = super.display_view(msg, view, options)
        // let promises = [];
        // this.models.forEach((model) => {
        //     // for(id in model.views) {

        //     // }
        //     if(model._real_update) {
        //         console.log('force update of ipyvolume')
        //         model._real_update()
        //     }
        // })
        result.then((view) => {
            let viewId = view.cid;
            if(viewIdSnapshots[viewId] == undefined) {
                viewIdSnapshots[viewId] = new defer()
            }
            let d = viewIdSnapshots[viewId];
            /*domtoimage.toPng(view.el).then(function (dataUrl) {
                var img = new Image();
                img.src = dataUrl;
                document.body.appendChild(img);
            }).catch(function (error) {
                console.error('oops, something went wrong!', error);
            });
            */
            view.on('displayed', () => {
                console.log('callbacks', (window as any)._webgl_update_callbacks)
            })
            

        })
        return result;
    }
    models: any;

    // async build_widgets() {
    //     let models = await this.build_models()
    //     window.models = models
    //     let element = document.body;
    //     let tags = element.querySelectorAll('script[type="application/vnd.jupyter.widget-view+json"]');
    //     for (let i=0; i!=tags.length; ++i) {
    //         let viewtag = tags[i];
    //         let widgetViewObject = JSON.parse(viewtag.innerHTML);
    //         let model_id = widgetViewObject.model_id;
    //         let model = models[model_id]
    //         let prev = viewtag.previousElementSibling;
    //         let widgetTag = document.createElement('div');
    //         widgetTag.className = 'widget-subarea';
    //         viewtag.parentElement.insertBefore(widgetTag, viewtag);
    //         this.display_model(undefined, model, { el : widgetTag });
    //     }
    // }
    // async build_models() {
    //     let comm_ids = await this._get_comm_info()
    //     let models = {};
    //     let widgets_info = await Promise.all(Object.keys(comm_ids).map(async (comm_id) => {
    //         var comm = await this._create_comm(this.comm_target_name, comm_id);
    //         return this._update_comm(comm);
    //     }));
    //     // do the creation of the widgets in parallel
    //     await Promise.all(widgets_info.map(async (widget_info) => {
    //             let promise = this.new_model({
    //                 model_name: widget_info.msg.content.data.state._model_name,
    //                 model_module: widget_info.msg.content.data.state._model_module,
    //                 model_module_version: widget_info.msg.content.data.state._model_module_version,
    //                 comm: widget_info.comm,
    //             }, widget_info.msg.content.data.state);
    //             let model = await promise;
    //             models[model.model_id] = model;
    //             return promise;
    //     }));
    //     return models
    // }

    // async _update_comm(comm) {
    //     return new Promise(function(resolve, reject) {
    //         comm.on_msg(async (msg) => {
    //             base.put_buffers(msg.content.data.state, msg.content.data.buffer_paths, msg.buffers);
    //             if (msg.content.data.method === 'update') {
    //                 resolve({comm: comm, msg: msg})
    //             }
    //         });
    //         comm.send({method: 'request_state'}, {})
    //     })
    // }

    // get onError() {
    //     return this._onError
    // }

    // registerWithKernel(kernel) {
    //     if (this._commRegistration) {
    //         this._commRegistration.dispose();
    //     }
    //     this._commRegistration = kernel.registerCommTarget(
    //         this.comm_target_name,
    //         (comm, message) =>
    //             this.handle_comm_open(new ShimmedComm(comm), message)
    //     );
    // }

    // display_view(msg, view, options) {
    //     const el = options.el || this.el;
    //     return Promise.resolve(view).then(view => {
    //         pWidget.Widget.attach(view.pWidget, el);
    //         view.on('remove', function() {
    //             console.log('view removed', view);
    //         });
    //         return view;
    //     });
    // }

    // loadClass(className, moduleName, moduleVersion) {
    //     if (moduleName === '@jupyter-widgets/output') {
    //         return Promise.resolve(outputWidgets).then(module => {
    //             if (module[className]) {
    //                 return module[className];
    //             } else {
    //                 return Promise.reject(
    //                     `Class ${className} not found in module ${moduleName}`
    //                 );
    //             }
    //         })
    //     } else {
    //         return super.loadClass(className, moduleName, moduleVersion)
    //     }
    // }

    // callbacks(view) {
    //     const baseCallbacks = super.callbacks(view)
    //     return {
    //         ...baseCallbacks,
    //         iopub: { output: (msg) => this._onError.emit(msg) }
    //     }
    // }

    // _create_comm(target_name, model_id, data, metadata) {
    //     const comm = this.kernel.connectToComm(target_name, model_id)
    //     if (data || metadata ) {
    //         comm.open(data, metadata)
    //     }
    //     return Promise.resolve(new ShimmedComm(comm))
    // }

    // _get_comm_info() {
    //     return this.kernel.requestCommInfo({ target: this.comm_target_name})
    //         .then(reply => reply.content.comms)
    // }
}
