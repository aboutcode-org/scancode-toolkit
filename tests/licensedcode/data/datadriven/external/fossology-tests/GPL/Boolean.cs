//
// (C) 2006-2007 The SharpOS Project Team (http://www.sharpos.org)
//
// Authors:
//	Mircea-Cristian Racasan <darx_kies@gmx.net>
//
// Licensed under the terms of the GNU GPL v3,
//  with Classpath Linking Exception for Libraries
//

using SharpOS.AOT.Attributes;
using SharpOS.Kernel.ADC;

namespace InternalSystem {
	[TargetNamespace ("System")]
	public struct Boolean {
#pragma warning disable 649
		internal byte Value;
#pragma warning restore 649

		public override string ToString ()
		{
			if (Value==0)
				return "false";
			else
				return "true";
		}
	}
}
