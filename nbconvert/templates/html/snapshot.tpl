{%- extends 'full.tpl' -%}

{% block ipywidgets %}
<script>
requirejs.config({
    waitSeconds : 30,
    baseUrl: 'resources',
    paths: {}
})

  require(['snapshot'], function(lib) {
    if (document.readyState === "complete") {
        lib.renderWidgets();
    } else {
        window.addEventListener('load', function() { lib.renderWidgets();});
    }
  });
</script>
{% endblock ipywidgets %}


{%- block data_widget_view scoped %}
{% set div_id = uuid4() %}
{% set datatype_list = output.data | filter_data_type %} 
{% set datatype = datatype_list[0]%} 
<div id="{{ div_id }}"></div>
<div class="output_subarea output_widget_view {{ extra_class }}" data-nb-cell-index="{{ cell_index }}" data-nb-output-index="{{ output_index }}">
    <script type="text/javascript">
    var element = $('#{{ div_id }}');
    </script>
    <script type="{{ datatype }}">
    {{ output.data[datatype] | json_dumps }}
    </script>
</div>
{%- endblock data_widget_view -%}

{% block data_html scoped -%}
<div class="output_html rendered_html output_subarea {{ extra_class }}"  data-nb-cell-index="{{ cell_index }}" data-nb-output-index="{{ output_index }}">
{{ output.data['text/html'] }}
</div>
{%- endblock data_html %}