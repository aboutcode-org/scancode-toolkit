---
name: "\U0001F41B License Detection Bug report"
about: Create a Report for a License Detection Bug
title: ''
labels: 'bug', 'license scan', 'new and improved data'
assignees: ''

---

<!-- 
Please fill out as much of the below template and delete unnecessary text.
Sample License Detection Bug Reports 
	- https://github.com/nexB/scancode-toolkit/issues/2126 
	- https://github.com/nexB/scancode-toolkit/issues/2266
Markdown Styling - https://commonmark.org/help/
-->

### Description

> Please leave a brief description of the License Detection Bug:


### Where to get the File/Package

> Link to Public Repository/Package Index, if there are multiple files that has license detection errors
> Also list some example files. If the bug is in a single file then link to the file. 



## Scan Reports 

> What scancode command was used?


> Scan Outputs (Preferably of a whole file in [json-pretty-print](https://scancode-toolkit.readthedocs.io/en/latest/cli-reference/output-format.html#json-pp-file))
> Note:- 
> If possible please use the `--license-text` and `--license-text-diagonostics` [command line options](https://scancode-toolkit.readthedocs.io/en/latest/cli-reference/basic-options.html#license-text-diagnostics-options) 
> as it helps understand which parts were wrongly matched and gives us more insight into the bug
> Upload your results.json file on this issue [like this](https://docs.github.com/en/enterprise/2.16/user/github/managing-your-work-on-github/file-attachments-on-issues-and-pull-requests)



### System/Scancode Configuration

> For bug reports, it really helps us to know:

* What OS are you running on? 
> (Windows/MacOS/Linux)


* What version of scancode-toolkit was used to generate the scan file?
> `./scancode --version` 


* What installation method was used to install/run scancode? 
> (pip/source download/other)


## Links to Rule or excerpts of Rule Texts (If Possible)

> Which Licenses/Rules were wrongly matched (if Applicable)
> 
> [Rule Directory](https://github.com/nexB/scancode-toolkit/tree/develop/src/licensedcode/data/rules) and [License Directory](https://github.com/nexB/scancode-toolkit/tree/develop/src/licensedcode/data/licenses)



## Select the Relevant Issue Category(s)

> [ ] - Unselected, [x] - Selected

-  [ ] Unknown License 
-  [ ] False Positive
-  [ ] Multiple Detections, Some Wrong
-  [ ] License Version Mismatch
-  [ ] New License
-  [ ] Change in License/Rule Attributes
-  [ ] Edit existing Rule
-  [ ] From [`scancode-results-analyzer`](https://github.com/nexB/scancode-results-analyzer) 


## Comments on the License Detection Bug

> What should have been detected instead, why is it a bug.



## Comments (if any) on How to Add a New Rule/Modify an existing Rule for solving this Bug

> Refer the documentation page at [Add new license](https://scancode-toolkit.readthedocs.io/en/latest/how-to-guides/add_new_license.html) and [Add new rule](https://scancode-toolkit.readthedocs.io/en/latest/how-to-guides/add_new_license_detection_rule.html) 


<!-- 
Your help makes ScanCode Toolkit better! We *deeply* appreciate your help in improving ScanCode Toolkit.
-->
