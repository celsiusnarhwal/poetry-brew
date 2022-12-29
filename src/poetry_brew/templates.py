from textwrap import dedent

from jinja2 import Environment, BaseLoader

env = Environment(loader=BaseLoader(), trim_blocks=True)

FORMULA_TEMPLATE = env.from_string(dedent("""\
    class {{ package.name }} < Formula
      include Language::Python::Virtualenv
      
      desc "{{ package.description }}"
      homepage "{{ package.homepage }}"
      url "{{ package.url }}"
      sha256 "{{ package.checksum }}"
      
      depends_on "python3"
      {% for dependency in dependencies %}depends_on "{{ dependency }}"
      {% endfor %}
      
    {% if resources %}
    {% for resource in resources %}
      resource "{{ resource.name }}" do
        url "{{ resource.url }}"
        sha256 "{{ resource.checksum }}"
      end

    {%  endfor %}
    {% endif %}

      def install
    {% if python == "python3" %}
        virtualenv_create(libexec, "python3")
    {% endif %}
        virtualenv_install_with_resources
      end
      test do
        false
      end
    end
    """))
