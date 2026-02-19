import os
from licensedcode.detection import get_detected_license_expression
from licensedcode.detection import DetectionCategory
from licensedcode.match import LicenseMatch
from licensedcode.models import Rule
from licensedcode.cache import get_licensing

def test_gpl_with_gcc_exception_uses_with_operator():
    """
    Test that GPL-3.0 and GCC-exception are combined with WITH instead of AND
    """
    licensing = get_licensing()
    
    gpl_rule = Rule(
        license_expression='gpl-3.0',
        text='GPL 3.0 text',
    )
    
    gcc_exception_rule = Rule(
        license_expression='gcc-exception-3.1',
        text='GCC exception text',
    )
    
    gpl_match = LicenseMatch(rule=gpl_rule, qspan=(0, 10), ispan=(0, 10))
    gcc_match = LicenseMatch(rule=gcc_exception_rule, qspan=(11, 20), ispan=(11, 20))
    
    matches = [gpl_match, gcc_match]
    
    detection_log, combined_expression = get_detected_license_expression(
        analysis=DetectionCategory.UNKNOWN_MATCH.value,
        license_matches=matches,
    )
    
    assert 'WITH' in combined_expression
    assert 'gpl-3.0 WITH gcc-exception-3.1' == combined_expression

if __name__ == '__main__':
    test_gpl_with_gcc_exception_uses_with_operator()
    print("Test passed!")
