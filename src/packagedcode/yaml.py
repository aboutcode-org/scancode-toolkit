import yaml
import attr
from packageurl import PackageUrl
from commoncode import filetype
from packagedcode import models

from packagedcode import models

@attr.s()
class YamlPackage(models.Package):
    metafiles = ('*.yaml',)
    extensions = ('.yaml',)
    """ default_type = ''
    """
    default_primary_language = 'dart'
    default_web_baseurl = 'https://dart.dev/tools/pub/pubspec
    default_download_baseurl = 'https://dart.dev/tools/pub/pubspec'
    default_api_baseurl = 'https://dart.dev/tools/pub/pubspec'

    @classmethod
    def recognize(cls, location):
        yield parse(location)

    def repository_homepage_url(self, baseurl=default_web_baseurl):
        return '{}/pods/{}'.format(baseurl, self.name)

    def repository_download_url(self):
        return '{}/archive/{}.zip'.format(self.homepage_url, self.version)

    def api_data_url(self):
        return self.homepage_url



def is_yaml(location):
    """
    Check if the file is a yaml file or not
    """
    return (filetype.is_file(location) 
            and location.endswith('.yaml'))

def parse_yaml(location):
    """
    code to parse yaml 
    """
    contents = io.open(location, encoding ='utf-8').readlines()
    with open(location,'r') as stream:
        yaml_data = yaml.load(stream)
    return yaml_data

def parse(location):
    if not is_yaml(location):
        return
    package_data = parse_yaml(location)
    return build_package(package_data)

def build_package(yaml_data):
    """
    Return a package object from a package data mapping ir None
    """
    name = yaml_data.get('name')
    version = yaml_data.get('version')
    declared_license = yaml_data.get('license')
    description = yaml_data.get('description')
    homepage_url = yaml_data.get('homepage_url')
    repository = yaml_data.get('repository')
    dependecies = yaml_data.get('dependencies')
    dev_dependecies = yaml_data.get('dev_dependencies')
    dependencies_overrides = yaml_get('dependencies_overrides')
    environment = yaml_data.get('environment')
    executables = yaml_data.get('executables')
    publish_to = yaml_data.get('publish_to')    
    authors = yaml_data.get('author') or []
    
    parties = []
    if authors:
        parties.append(
                models.Party(
                        type=models.party_person,
                        name=', '.join(authors),
                        email=', '.join(email),
                        role='author'
                    )
                )
    dependencies = yaml_data.get('dependencies')
    package_dependencies = []
    if dependencies:
        for dep_name, dep_version in dependencies.items():
            package_dependencies.append(
                    models.DependentPackage(
                            purl=PackageURL(
                                    """
                                    need to specify the type
                                    """
                                    type='',
                                            name=dep_name).toString(),
                                            scope='dependencies',
                                            is_runtime=True,
                                            is_optional=True,
                                            requirement=dep_version,
                                            )
                            )
   """ if dev_dependencies:
                for dep_name, dep_version in dev_dependencies.items():
                    package_dependencies.append(
                            models.DependentPackage(
                                    purl=PackageURL(
                                            """
                                            need to specify the type again
                                            """
                                            type='',
                                            name=dep_name).toString(),
                                            scope='dev_dependencies',
                                            is_runtime=True,
                                            is_optional=True,
                                            requirement=dep_version,
                                            )
                            )
                                    should add the code for dev_dependencies or not ???
                                    """
        
    package = YamlPackage(
            name = name,
            version = version,
            vcs_url = source,
            source_packages=list(source.split('\n')),
            description=desciption,
            declared_license=declared_license,
            homepage_url=homepage_url,
            parties=parties,
            dependencies=package_dependencies
            )
    return package
     
    