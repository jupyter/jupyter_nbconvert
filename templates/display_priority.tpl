{%- extends 'null.tpl' -%}

{#display data priority#}


{%- block data_priority scoped -%}
    {%- for type in output | filter_data_type -%}
        {%- if type in ['pdf']%}
            {%- block data_pdf -%}
                ->> pdf
            {%- endblock -%}
        {%- endif -%}
        {%- if type in ['svg']%}
            {%- block data_svg -%}
                ->> svg
            {%- endblock -%}
        {%- endif -%}
        {%- if type in ['png']%}
            {%- block data_png -%}
                ->> png
            {%- endblock -%}
        {%- endif -%}
        {%- if type in ['html']%}
            {%- block data_html -%}
                ->> html
            {%- endblock -%}
        {%- endif -%}
        {%- if type in ['jpeg']%}
            {%- block data_jpg -%}
                ->> jpg
            {%- endblock -%}
        {%- endif -%}
        {%- if type in ['text']%}
            {%- block data_text -%}
                ->> text
            {%- endblock -%}
        {%- endif -%}

        {%- if type in ['latex']%}
            {%- block data_latex -%}
                ->> latext
            {%- endblock -%}
        {%- endif -%}
    {%- endfor -%}
{%- endblock data_priority -%}
