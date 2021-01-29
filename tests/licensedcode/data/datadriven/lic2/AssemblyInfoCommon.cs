//---------------------------------------------------------------------
// <copyright file="AssemblyInfoCommon.cs" company="Microsoft">
//      Copyright (C) Microsoft Corporation. All rights reserved. See License.txt in the project root for license information.
// </copyright>
//---------------------------------------------------------------------

using System;
using System.Reflection;
using System.Resources;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Runtime.Versioning;
using System.Security;

#if !SUPPRESS_PORTABLELIB_TARGETFRAMEWORK_ATTRIBUTE
#if PORTABLELIB
#if ODATA_CLIENT
[assembly: TargetFramework(".NETPortable,Version=v4.5,Profile=Profile259", FrameworkDisplayName = ".NET Portable Subset")]
#else
[assembly: TargetFramework(".NETPortable,Version=v4.0,Profile=Profile328", FrameworkDisplayName = ".NET Portable Subset")]
#endif
#endif
#endif

[assembly: AssemblyCompany("Microsoft Corporation")]
// If you want to control this metadata globally but not with the VersionProductName property, hard-code the value below.
// If you want to control this metadata at the individual project level with AssemblyInfo.cs, comment-out the line below.
// If you leave the line below unchanged, make sure to set the property in the root build.props, e.g.: <VersionProductName Condition="'$(VersionProductName)'==''">Your Product Name</VersionProductName>
// [assembly: AssemblyProduct("%VersionProductName%")]
[assembly: AssemblyCopyright("Copyright (c) Microsoft Corporation. All rights reserved.")]
[assembly: AssemblyTrademark("Microsoft and Windows are either registered trademarks or trademarks of Microsoft Corporation in the U.S. and/or other countries.")]
[assembly: AssemblyCulture("")]
#if (DEBUG || _DEBUG)
[assembly: AssemblyConfiguration("Debug")]
#endif

#if ASSEMBLY_ATTRIBUTE_PRODUCT_VS
[assembly: AssemblyProduct("Microsoft (R) Visual Studio (R) 2010")]
#else
[assembly: AssemblyProduct("Microsoft® .NET Framework")]
#endif

#if ASSEMBLY_ATTRIBUTE_CLS_COMPLIANT
[assembly: CLSCompliant(true)]
#else
[assembly: CLSCompliant(false)]
#endif

#if ASSEMBLY_ATTRIBUTE_COM_VISIBLE
[assembly: ComVisible(true)]
#else
[assembly: ComVisible(false)]
#endif

#if ASSEMBLY_ATTRIBUTE_COM_COMPATIBLE_SIDEBYSIDE
[assembly:ComCompatibleVersion(1,0,3300,0)]
#endif

#if ASSEMBLY_ATTRIBUTE_ALLOW_PARTIALLY_TRUSTED_CALLERS
[assembly: AllowPartiallyTrustedCallers]
#else
#if ASSEMBLY_ATTRIBUTE_CONDITIONAL_APTCA_L2
[assembly:AllowPartiallyTrustedCallers(PartialTrustVisibilityLevel=PartialTrustVisibilityLevel.NotVisibleByDefault)]
#endif
#endif

#if ASSEMBLY_ATTRIBUTE_TRANSPARENT_ASSEMBLY
[assembly: SecurityTransparent]
#endif

#if !SUPPRESS_SECURITY_RULES
#if SECURITY_MIGRATION && !ASSEMBLY_ATTRIBUTE_CONDITIONAL_APTCA_L2
#if ASSEMBLY_ATTRIBUTE_SKIP_VERIFICATION_IN_FULLTRUST
[assembly: SecurityRules(SecurityRuleSet.Level1, SkipVerificationInFullTrust = true)]
#else
[assembly: SecurityRules(SecurityRuleSet.Level1)]
#endif
#else
#if ASSEMBLY_ATTRIBUTE_SKIP_VERIFICATION_IN_FULLTRUST
[assembly: SecurityRules(SecurityRuleSet.Level2, SkipVerificationInFullTrust = true)]
#else
[assembly: SecurityRules(SecurityRuleSet.Level2)]
#endif
#endif
#endif

[assembly:NeutralResourcesLanguageAttribute("en-US")]
