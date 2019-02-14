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
