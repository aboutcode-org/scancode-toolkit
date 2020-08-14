#
# Copyright (c) 2018 nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# Data generated with ScanCode require an acknowledgment.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# When you publish or redistribute any data created with ScanCode or any ScanCode
# derivative work, you must accompany this data with the following acknowledgment:
#
#  Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
#  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
#  ScanCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

from typecode.language_model import score
import yaml
import os
import re
import io

MAX_LEN = 209   # default sequence lenghth model was trained on'

data_dir = os.path.join(os.path.dirname(__file__), 'data')
tokens_path = os.path.join(data_dir, "token_indexes.yml")  # used to map words to indexes

with open(tokens_path, 'r') as stream:
    token_indexes = yaml.safe_load(stream)

classes = ['C', 'C#', 'C++', 'CoffeeScript', 'Common Lisp',
           'Component Pascal', 'D', 'Erlang', 'F#', 'Forth', 'Fortran', 'GAP',
           'GLSL', 'Gosu', 'IDL', 'JavaScript', 'Limbo', 'Lua', 'MATLAB',
           'Makefile', 'Mathematica', 'Mercury', 'Moocode', 'NewLisp',
           'Objective-C', 'PHP', 'Pascal', 'Perl', 'PicoLisp', 'Prolog',
           'Python', 'R', 'Rebol', 'Ruby', 'Scala', 'Scilab', 'SuperCollider',
           'VBA', 'Vim script']

def text_to_vector(text):
    """
    Converts raw text to vector to input to language classifier.
    """
    input_vector = [0] * MAX_LEN
    content_tokens = re.sub(' +',' '," ".join(re.split(r'[^\w]', re.sub(re.compile("/\*.*?\*/",re.DOTALL ) ,"" , text)))).lower().split(' ')
    idx = 0
    for token in content_tokens:
        if idx > MAX_LEN - 1:
            break
        token_index = token_indexes.get(token)
        if token_index:
            input_vector[idx] = token_index
            idx += 1
        else:
            continue
    return input_vector
    
def classify_language(location, from_laguages):

    """
    Classifies programming language based on file content from the given subset of 'from_laguages'.
    Returns a single programming language as classified by language classifier.
    """
    with io.open(location, 'r', encoding='utf-8') as f:
        content = f.read(2048)

    indices = list(map(classes.index, from_laguages))
    probabilities = score(text_to_vector(content))
    probabilities = list(map(probabilities.__getitem__, indices))
    predicted_language = from_laguages[probabilities.index(max(probabilities))]

    return predicted_language
