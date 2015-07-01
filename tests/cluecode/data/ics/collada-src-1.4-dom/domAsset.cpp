/*
* Copyright 2006 Sony Computer Entertainment Inc.
*
* Licensed under the MIT Open Source License, for details please see license.txt or the website
	cm->appendChild( mea );

	mea = new daeMetaElementAttribute( meta, cm, 3, 0, 1 );
	mea->setName( "copyright" );
	mea->setOffset( daeOffsetOf(domAsset::domContributor,elemCopyright) );
	mea->setElementType( domAsset::domContributor::domCopyright::registerElement(dae) );
	cm->appendChild( mea );

}

daeElementRef
domAsset::domContributor::domCopyright::create(DAE& dae)
{
	domAsset::domContributor::domCopyrightRef ref = new domAsset::domContributor::domCopyright(dae);
	return ref;
}


daeMetaElement *
domAsset::domContributor::domCopyright::registerElement(DAE& dae)
{
	daeMetaElement* meta = dae.getMeta(ID());

	meta = new daeMetaElement(dae);
	dae.setMeta(ID(), *meta);
	meta->setName( "copyright" );
	meta->registerClass(domAsset::domContributor::domCopyright::create);

	meta->setIsInnerClass( true );
		daeMetaAttribute *ma = new daeMetaAttribute;
		ma->setName( "_value" );
		ma->setType( dae.getAtomicTypes().get("xsString"));
		ma->setOffset( daeOffsetOf( domAsset::domContributor::domCopyright , _value ));
		ma->setContainer( meta );
		meta->appendAttribute(ma);
	}

	meta->setElementSize(sizeof(domAsset::domContributor::domCopyright));
	meta->validate();
