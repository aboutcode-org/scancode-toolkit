================
Kit de Ferramentas ScanCode
================
Um típico projeto de software costuma utilizar centenas de pacotes terceiros. 
Informação sobre origem e licença nem sempre são faceis de se achar, e nem sempre são normalizadas: 
ScanCode descobre e normaliza esses dados para você.

Por que o ScanCode é melhor?
=======================

- Por ser uma **ferramenta de linha de comando standalone**, ScanCode é **fácil de instalar**, rodar
  e embutir em seu processo de pipeline CI/CD. Funciona nos sistemas **Windows, macOS e Linux**.

- ScanCode é **usado em diversos projetos e organizações**, como `Eclipse
  Foundation <https://www.eclipse.org>`_, `OpenEmbedded.org <https://www.openembedded.org>`_,
  the `FSF <https://www.fsf.org>`_, `OSS Review Toolkit <http://oss-review-toolkit.org>`_, 
  `ClearlyDefined.io <https://clearlydefined.io/>`_,
  `RedHat Fabric8 analytics <https://github.com/fabric8-analytics>`_ e muitas outras.

- ScanCode detecta licenças, direitos autorais, manifestos de pacotes, dependencias
  diretas e outras, em ambos código fonte e arquivos binários

- ScanCode provê a **ferramenta de detecção de licenças mais precisa** e faz uma
  comparação completa entre a base de dados de textos de licença e o seu código,
  ao invés de depender apenas em padrões regex ou busca probabilisticas, edit
  distance ou aprendizado de máquina

- Escrito em Python, ScanCode é **fácilmente expendível com plugins** para contribuir 
  novos e melhorados scanners, sumarização de dados, parsers de manifestos de pacotes
  e novas saídas.

- Você pode salvar seus resultados explorados como **JSON, HTML, CSV ou SPDX**, e pode
  usar o companheiro `ScanCode workbench GUI app <https://github.com/nexB/scancode-workbench>`_
  para revisar e exibir resultados de análises, estatísticas e gráficos.

- ScanCode é **mantido ativamente** e tem uma **crescente comunidade de usuários**.

- ScanCode é altamente **testado** com um suite de testes automatizado contendo mais de **8000 tests**

Veja nosso roadmap para funcionalidades futuras:
https://github.com/nexB/scancode-toolkit/wiki/Roadmap

Status de Build e Test
======================

+-------+--------------+-----------------+--------------+
|Branch | **Cobertura**| **Linux/macOS** | **Windows**  |
+=======+==============+=================+==============+
|Master | |master-cov| | |master-posix|  | |master-win| |
+-------+--------------+-----------------+--------------+
|Develop| |devel-cov|  | |devel-posix|   | |devel-win|  |
+-------+--------------+-----------------+--------------+


Guia de Início Rápido
===========

Instalar o Python 2.7, para então baixar e extrair a última release do ScanCode
do repositório https://github.com/nexB/scancode-toolkit/releases/ 

Depois rodar ``./scancode -h`` para ajuda.


Instalação
============

Pre-requisitos:

* No Windows, siga os passos de `Instruções Compreensivas de Instalação
  <https://github.com/nexB/scancode-toolkit/wiki/Comprehensive-Installation>`_.
  Tenha certeza de utilizar o Python 2.7 de 32 bits, disponibilizado em
  https://www.python.org/ftp/python/2.7.15/python-2.7.15.msi

* No macOS, instalar Python 2.7 disponibilizado em
  https://www.python.org/ftp/python/2.7.15/python-2.7.15-macosx10.6.pkg

  Depois, baixar e extrair a última release do ScanCode do repositório
  https://github.com/nexB/scancode-toolkit/releases/

* No Linux, instalar o Python 2.7 "devel" e os seguintes pacotes, utilizando
  o gerenciador de pacotes da sua distribuição:

  * No Ubuntu 14, 16 e 18, use:
    ``sudo apt-get install python-dev xz-utils zlib1g libxml2-dev libxslt1-dev bzip2``

  * No Debian e distribuições baseadas em Debian, use:
    ``sudo apt-get install python-dev xz-utils zlib1g libxml2-dev libxslt1-dev libbz2-1.0``

  * Nas distribuições RPM, use:
    ``sudo yum install python-devel xz-libs zlib libxml2-devel libxslt-devel bzip2-libs``

  * No Fedora 22 e posteriores, use:
    ``sudo dnf install python-devel xz-libs zlib libxml2-devel libxslt-devel bzip2-libs``

* Siga os passos de `Instruções Compreensivas de Instalação
  <https://github.com/nexB/scancode-toolkit/wiki/Comprehensive-Installation>`_
  para instruções adicionais.


Depois, baixar e extrair a última release do ScanCode do repositório
https://github.com/nexB/scancode-toolkit/releases/


Abra uma janela de terminal, vá até o diretório em que o ScanCode foi extraído
e rode esse comando para exibir ajuda. O ScanCode irá se configurar sozinho, se necessário::

    ./scancode --help

Você pode rodar uma análise de exemplo exibida na tela como JSON::

    ./scancode -clip --json-pp - samples

Veja mais comandos de exemplos::

    ./scancode --examples

Extração de Arquivos
===================

Os arquivos existentes em uma base de código devem ser extraídos antes de rodar uma análise:
o ScanCode não extrai arquivos de tarballs, arquivos zip, etc. como parte do scan.
A utilidade agrupada `extracode` é um extrator de arquivos quase universal.
Por exemplo, esse comando irá extrair recursivamente mytar.tar.bz2 tarball no
diretório mytar.tar.bz2-extract::

    ./extractcode mytar.tar.bz2


Documentação & FAQ
===================

https://github.com/nexB/scancode-toolkit/wiki

Veja também https://aboutcode.org para projetos e ferramentas relacionados.


Suporte
=======

Se você tiver um problema, uma sugestão ou achou um bug, por favor, crie um ticket em:
https://github.com/nexB/scancode-toolkit/issues

Para discussões e chats, temos:

* Um canal oficial no Gitter para chat web-based, em https://gitter.im/aboutcode-org/discuss
  Gitter também é acessivel por meio de uma ponte IRC, em https://irc.gitter.im/

* Um canal oficial do IRC `#aboutcode` no freenode (server chat.freenode.net). 
  Esse canal recebe notificações de build e commit e pode acabar sendo um pouco barulhento.
  Você pode utilizar seu client IRC favorito ou web chat em https://webchat.freenode.net/


Código Fonte e Downloads
=========================

* https://github.com/nexB/scancode-toolkit.git
* https://github.com/nexB/scancode-toolkit/releases
* https://pypi.org/project/scancode-toolkit/
* https://github.com/nexB/scancode-thirdparty-src.git


Licença
=======

* Apache-2.0 com um conhecimento necessário para acompanhar a saída da análise.
* Domínio público CC-0 para datasets de referência.
* Multiplas licenças (GPL2/3, LGPL, MIT, BSD, etc.) para componentes terceiros.

Veja o arquivo NOTICE e os arquivos .ABOUT que documentam a origem e licença dos
códigos terceiros utilizados no ScanCode, para informações adicionais


.. |master-cov| image:: https://codecov.io/gh/nexB/scancode-toolkit/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/nexB/scancode-toolkit/branch/master
    :alt: Master branch test coverage (Linux)
.. |devel-cov| image:: https://codecov.io/gh/nexB/scancode-toolkit/branch/develop/graph/badge.svg
    :target: https://codecov.io/gh/nexB/scancode-toolkit/branch/develop
    :alt: Develop branch test coverage (Linux)

.. |master-posix| image:: https://api.travis-ci.org/nexB/scancode-toolkit.png?branch=master 
    :target: https://travis-ci.org/nexB/scancode-toolkit
    :alt: Linux Master branch tests status
.. |devel-posix| image:: https://api.travis-ci.org/nexB/scancode-toolkit.png?branch=develop
    :target: https://travis-ci.org/nexB/scancode-toolkit
    :alt: Linux Develop branch tests status

.. |master-win| image:: https://ci.appveyor.com/api/projects/status/4webymu0l2ip8utr/branch/master?png=true
    :target: https://ci.appveyor.com/project/nexB/scancode-toolkit
    :alt: Windows Master branch tests status
.. |devel-win| image:: https://ci.appveyor.com/api/projects/status/4webymu0l2ip8utr/branch/develop?png=true
    :target: https://ci.appveyor.com/project/nexB/scancode-toolkit
    :alt: Windows Develop branch tests status
