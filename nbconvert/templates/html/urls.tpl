{# default configuration #}
{% set cdn1_base = 'https://cdnjs.cloudflare.com/ajax/libs/' %}
{% set default_cdn      = {
  'mathjax_url'      : cdn1_base ~ 'mathjax/2.7.5/latest.js?config=TeX-AMS_HTML',
  'require_js_url'   : cdn1_base ~ 'require.js/2.3.6/require.min.js',
  'jquery_url'       : cdn1_base ~ 'jquery/3.3.1/jquery.min.js',
  'reveal_js_url'    : cdn1_base ~ 'reveal.js/3.7.0/js/reveal.min.js',
  'font_awesome_url' : cdn1_base ~ 'font-awesome/4.7.0/css/font-awesome.css',
  } %}

{# alternative external resources - not yet implemented as switch #}
{% set cdn2_base = 'https://cdn.jsdelivr.net/npm/' %}
{% set alternative_cdn      = {
  'mathjax_url'      : cdn2_base ~ 'mathjax@2.7.5/unpacked/MathJax.min.js',
  'require_js_url'   : 'https://requirejs.org/docs/release/2.3.6/minified/require.js',
  'jquery_url'       : cdn2_base ~ 'jquery@3.3.1/dist/jquery.min.js',
  'reveal_js_url'    : cdn2_base ~ 'reveal.js@3.7.0/js/reveal.min.js',
  'font_awesome_url' : 'https://stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css',
  } %}

{# set local paths for resources #}
{% set libs_dir  = 'libs/' %}
{% set local_paths      = {
  'mathjax_url'      : libs_dir ~ 'mathjax/2.7.5/latest.js?config=TeX-AMS_HTML',
  'require_js_url'   : libs_dir ~ 'require.min.js',
  'jquery_url'       : libs_dir ~ 'jquery.min.js',
  'reveal_js_url'    : libs_dir ~ 'reveal.min.js',
  'font_awesome_url' : libs_dir ~ 'font-awesome.css',
  } %}

{% set all_urls = {
  'default_cdn'     : default_cdn ,
  'alternative_cdn' : alternative_cdn ,
  'local_paths'     : local_paths ,
  } %}

{% set empty_attr     = {
  'mathjax_attr'      : '',
  'require_js_attr'   : '',
  'jquery_attr'       : '',
  'reveal_js_attr'    : '',
  'font_awesome_attr' : '',
  } %}

{% set sri_attr     = {
'mathjax_attr'      : 'integrity="sha256-WUED7NFzpsmHtLO7bswSz4JSfkhE+cD4ncKeOznwFSY= sha384-paYjEtNXu9X/q6SBQB9EivI88vKEc/TiZWUaaH5j2Hi4vAOnVYmcahbzUELr3LHw sha512-BlZeGCIONWMdv9uCBB3I3hpY94r8I2e4DdNxyl4OOHYg0Y/LwwWDC4ioJr9vRaLNHwQG0oHiFdmqt7UaTCAZ0A==" crossorigin="anonymous"',
'require_js_attr'   : 'integrity="sha256-1fEPhSsRKlFKGfK3eO710tEweHh1fwokU5wFGDHO+vg= sha384-38qS6ZDmuc4fn68ICZ1CTMDv4+Yrqtpijvp5fwMNdbumNGNJ7JVJHgWr2X+nJfqM sha512-c3Nl8+7g4LMSTdrm621y7kf9v3SDPnhxLNhcjFJbKECVnmZHTdo+IRO05sNLTH/D3vA6u1X32ehoLC7WFVdheg==" crossorigin="anonymous"',
'jquery_attr'       : 'integrity="sha256-FgpCb/KJQlLNfOu91ta32o/NMZxltwRo8QtmkMRdAu8= sha384-tsQFqpEReu7ZLhBV2VZlAu7zcOV+rXbYlF2cqB8txI/8aZajjp4Bqd+V6D5IgvKT sha512-+NqPlbbtM1QqiK8ZAo4Yrj2c4lNQoGv8P79DPtKzj++l5jnN39rHA/xsqn8zE9l0uSoxaCdrOgFs6yjyfbBxSg==" crossorigin="anonymous"',
'reveal_js_attr'    : 'integrity="sha256-Xr6ZH+/kc7hDVReZLO5khBknteLqu5oen/xnSraXrVk= sha384-YSZJq04Xw1k1QeTgkujYtdAjgN/sspQx01Qx4JPksOst7V7juBOa/XBwsIK+mJ7c sha512-47qp+bUV262nwngjB+lBR1txpTKevoQKlz3d1+0uvu6Zly3Q+Y+tR19xDDk4NnutJ9vu6uojPXQS4S3sOB06qw==" crossorigin="anonymous"',
'font_awesome_attr' : 'integrity="sha256-NuCn4IvuZXdBaFKJOAcsU2Q3ZpwbdFisd5dux4jkQ5w= sha384-FckWOBo7yuyMS7In0aXZ0aoVvnInlnFMwCv77x9sZpFgOonQgnBj1uLwenWVtsEj sha512-5A8nwdMOWrSz20fDsjczgUidUBR8liPYU+WymTZP1lmY9G6Oc7HlZv156XqnsgNUzTyMefFTcsFH/tnJE/+xBg==" crossorigin="anonymous"',
  } %}

{% set all_attr = {
  'empty_attr'  : empty_attr,
  'sri_attr'    : sri_attr,
  } %}