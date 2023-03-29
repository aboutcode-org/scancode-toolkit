{% block content %}

.. _supported_packages:

Supported package manifests and package datafiles
-------------------------------------------------

Scancode supports a wide variety of package manifests, lockfiles
and other package datafiles containing package and dependency
information.

This documentation page is generated automatically from available package
parsers in scancode-toolkit during documentation builds.


.. list-table:: Supported Package Parsers
   :widths: 10 10 20 10 10 2
   :header-rows: 1

   * - Description
     - Path Patterns
     - Package type
     - Datasource ID
     - Primary Language
     - Documentation URL
   {% for package_data in all_available_packages -%}
   * - {% if package_data.description %}{{ package_data.description }}{% else %}{{"None"}}{% endif %}
     - {% if package_data.path_patterns %}{{ package_data.path_patterns }}{% else %}{{"None"}}{% endif %}
     - {{ package_data.package_type }}
     - {{ package_data.datasource_id }}
     - {{ package_data.default_primary_language }}
     - {% if package_data.documentation_url %}{{ package_data.documentation_url }}{% else %}{{"None"}}{% endif %}
   {% endfor %}{% endblock %}