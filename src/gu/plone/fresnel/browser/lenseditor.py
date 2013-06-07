import logging

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from five import grok
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.directives import form

from z3c.form import button
from z3c.form.browser.textarea import TextAreaFieldWidget
from zope import schema
from zope.component import getUtility
from zope.event import notify

from ordf.graph import Graph, ConjunctiveGraph
from plone.registry.interfaces import IRegistry
from cStringIO import StringIO
from gu.plone.rdf import _, LOG
from gu.z3cform.rdf.interfaces import IORDF

from z3c.form.interfaces import NOT_CHANGED
from gu.plone.rdf.interfaces import IRDFSettings

# TODO: store original text as annotation
# TODO: retrieve annotation instead

# NOTES:
# local = ConjunctiveGraph( IAnnotations(context)['gu.plone.rdf'] )
# see applyChanges for how to use this

class IFresnelLensEditForm(form.Schema):
    form.widget( lens=TextAreaFieldWidget )
    lens = schema.Text(
        title=_(u'Fresnel Lens'),
        required=False,
    )

#

master = """
@prefix rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#> .
@prefix rdfg:    <http://www.w3.org/2004/03/trix/rdfg-1/> .
@prefix owl:     <http://www.w3.org/2002/07/owl#> .
@prefix xsd:     <http://www.w3.org/2001/XMLSchema#> .
@prefix fresnel: <http://www.w3.org/2004/09/fresnel#> .
@prefix foaf:    <http://xmlns.com/foaf/0.1/> .
@prefix ordf:    <http://purl.org/NET/ordf/> .
@prefix opmv:    <http://purl.org/net/opmv/ns#> .
@prefix time:    <http://www.w3.org/2006/time#> .
@prefix dc:      <http://purl.org/dc/elements/1.1/> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix dcmitype: <http://purl.org/dc/dcmitype/> .
@prefix marcrel: <http://www.loc.gov/loc.terms/relators/> .
@prefix cld:     <http://purl.org/cld/terms/> .
@prefix cooee:   <http://ns.ausnc.org.au/corpus/COOEE/> .
@prefix ausnc:   <http://ns.ausnc.org.au/schemas/ausnc_md_model/> .
@prefix :        <http://namespaces.gu.edu.au/z3cform/fresnel#> .
@prefix source:  <http://aperture.semanticdesktop.org/ontology/2007/08/12/source#> .
@prefix sourceformat: <http://aperture.semanticdesktop.org/ontology/sourceformat#> .
@prefix olac:    <http://www.language-archives.org/OLAC/1.1/> .
@prefix addrschema: <http://schemas.talis.com/2005/address/schema#> .
@prefix dbpedia: <http://dbpedia.org/resource/> .
@prefix gcsause: <http://ns.ausnc.org.au/corpus/gcsause/> .
@prefix ace:     <http://ns.ausnc.org.au/corpus/ACE/> .
@prefix bibo:    <http://purl.org/ontology/bibo/> .
@prefix ands: <http://purl.org/ands/ontologies/vivo/> .
@prefix vivo: <http://vivoweb.org/ontology/core#> .
@prefix for08: <http://purl.org/asc/1297.0/2008/for/> .
@prefix cs: <http://purl.org/vocab/changeset/schema#> .
@prefix locn: <http://www.w3.org/ns/locn#> .
@prefix z3c: <http://namespaces.zope.org/z3c/form#> .
@prefix cvocab: <http://namespaces.griffith.edu.au/collection_vocab#> .
@prefix trel: <http://namespaces.terranova.org.au/relation#> .
@prefix ttyp: <http://namespaces.terranova.org.au/type#> .
@prefix tsec: <http://namespaces.terranova.org.au/sector#> .

:DefaultGroup a fresnel:Group ;
    .
  
:AllLens a fresnel:Lens ;
    rdfs:label "Generic All Lens" ;
    #fresnel:classLensDomain owl:Thing ;
    fresnel:group :DefaultGroup ;
    fresnel:hideProperties ( rdf:type ) ;
    fresnel:showProperties ( 
                             dcterms:title
                             dcterms:description
                             fresnel:allProperties ) ;
    .

:ItemLens a fresnel:Lens ;
    rdfs:label "Item metadata" ;
    fresnel:classLensDomain cvocab:Item ;
    fresnel:group :DefaultGroup ;
    #fresnel:showProperties ( fresnel:allProperties ) ;
    fresnel:hideProperties ( rdf:type ) ;
    fresnel:showProperties ( 
                             dcterms:title
                             dcterms:description
                             ) ;

    .

:PersonLens a fresnel:Lens ;
    rdfs:label "Person metadata" ;
    fresnel:classLensDomain foaf:Person ;
    fresnel:group :DefaultGroup ;
    fresnel:hideProperties ( rdf:type ) ;
    fresnel:showProperties ( rdfs:label
                             foaf:givenName
                             foaf:familyName
                             foaf:img  # might have to use a sublens here?
                             ands:nla
                             ands:isMemberOf
                             ands:isCollectorOf
                             ands:isOwnerOf
                             ands:isParticipantIn
                             ands:isPointOfContactFor
                             ands:streetAddress
                             ands:postalAddress
                             ands:enriches
                             #[ fresnel:property ands:streetAddress ;
                             #   rdf:type fresnel:PropertyDescription ;
                             #   fresnel:sublens :AddressLens ;
                             #]

                             fresnel:allProperties
                           ) ;
    . 

:RelatedInformationLens a fresnel:Lens ;
    rdfs:label "Related Information" ;
    fresnel:classLensDomain vivo:InformationResource ;
    fresnel:group :DefaultGroup ;
    fresnel:hideProperties ( rdf:type ) ;
    fresnel:showProperties ( ands:relatedInformationType
                             dcterms:identifier 
                             rdfs:label
                             dcterms:description
                            ) ;
    .

:CollectionLens a fresnel:Lens ;
    rdfs:label "Collection metadata" ;
    fresnel:classLensDomain cvocab:Collection ;
    fresnel:group :DefaultGroup ;
    fresnel:hideProperties ( 
                             rdf:type
                             time:hasBeginning
                             time:hasEnd
                             dcterms:identifier
                             dcterms:type
                             vivo:hasSubjectArea
                             dcterms:spatial
                             dcterms:temporal
                             dcterms:license
                           ) ;
    fresnel:showProperties ( 
                             # rdfs:label
                             dcterms:title
                             dcterms:description

                             # Fieldset: Basic Information
                             [ rdf:type z3c:PropertyGroup ;
                               z3c:propertyGroup :CollectionBasicInformationFieldSet ;
                             ]

                             # Fieldset: Attribution
                             [ rdf:type z3c:PropertyGroup ;
                               z3c:propertyGroup :CollectionAttributionFieldSet ;
                             ]

                             # Fieldset: Description
                             [ rdf:type z3c:PropertyGroup ;
                               z3c:propertyGroup :CollectionDescriptionFieldSet ;
                             ]

                             # Fieldset: Contents
                             [ rdf:type z3c:PropertyGroup ;
                               z3c:propertyGroup :CollectionContentsFieldSet ;
                             ]
                             
                             # Fieldset: Related
                             [ rdf:type z3c:PropertyGroup ;
                               z3c:propertyGroup :CollectionRelatedFieldSet ;
                             ]

                             # Fieldset: Permissions
                             [ rdf:type z3c:PropertyGroup ;
                               z3c:propertyGroup :CollectionPermissionsFieldSet ;
                             ]

                             # Fieldset: Submission
                             [ rdf:type z3c:PropertyGroup ;
                               z3c:propertyGroup :CollectionSubmissionFieldSet ;
                             ]
                                                          
                             fresnel:allProperties 
                            ) ;
    .

:CollectionBasicInformationFieldSet a z3c:PropertyGroup ;
    rdfs:label "Basic Info" ;
    rdfs:comment "Basic information describing the object" ;
    fresnel:group :DefaultGroup ;
    fresnel:showProperties (
        time:hasBeginning
        time:hasEnd
        dcterms:identifier
        dcterms:abstract
        ) ;
    .

:CollectionAttributionFieldSet a z3c:PropertyGroup ;
    rdfs:label "Attribution" ;
    rdfs:comment "Attribution information for the object" ;
    fresnel:group :DefaultGroup ;
    fresnel:showProperties (
        # Primary Contact
        # Associated GU Members
        # Associated External People
        # Related Projects
        ) ;
    .

:CollectionDescriptionFieldSet a z3c:PropertyGroup ;
    rdfs:label "Description" ;
    rdfs:comment "Description details about the collection" ;
    fresnel:group :DefaultGroup ;
    fresnel:showProperties (
        dcterms:type # Format
        # Work Type
        vivo:hasSubjectArea # FoR Codes
        # Keywords
        
        ## Spatial
        # Place Name
        # Selection
        # Coordinates
        dcterms:spatial
        
        ## Time Periods
        # From
        # To
        # Alternate descriptor
        dcterms:temporal

        # Collection Type
        ) ;
    .

:CollectionContentsFieldSet a z3c:PropertyGroup ;
    rdfs:label "Contents" ;
    rdfs:comment "Attribution information for the object" ;
    fresnel:group :DefaultGroup ;
    fresnel:showProperties (
        
        ) ;
    .

:CollectionRelatedFieldSet a z3c:PropertyGroup ;
    rdfs:label "Related" ;
    rdfs:comment "Attribution information for the object" ;
    fresnel:group :DefaultGroup ;
    fresnel:showProperties (
        ) ;
    .

:CollectionPermissionsFieldSet a z3c:PropertyGroup ;
    rdfs:label "Permissions" ;
    rdfs:comment "Attribution information for the object" ;
    fresnel:group :DefaultGroup ;
    fresnel:showProperties (
        dcterms:license 
        ) ;
    .
    
:CollectionSubmissionFieldSet a z3c:PropertyGroup ;
    rdfs:label "Submission" ;
    rdfs:comment "Attribution information for the object" ;
    fresnel:group :DefaultGroup ;
    fresnel:showProperties (
        ) ;
    .


:AddressLens a fresnel:Lens ;
    rdfs:label "Address information" ;
    fresnel:classLensDomain vivo:Address ;
    fresnel:group :DefaultGroup ;
    fresnel:hideProperties ( rdf:type ) ;
    fresnel:showProperties ( vivo:address1
                             vivo:address2
                             vivo:address3
                             vivo:addressCity
                             vivo:addressState
                             vivo:addressPostalCode
                             vivo:addressCountry
                           )
    .


# FIXME: all FieldSets should have a fresnel:group property
:ItemBasicInformationFieldSet a z3c:PropertyGroup ;
    rdfs:label "Further Information" ;
    rdfs:comment "Basic information describing the object" ;
    fresnel:group :DefaultGroup ;
    fresnel:showProperties (
        trel:hasDocumentType
        # TODO: identifier could be more specific if necessary.
        dcterms:identifier
        dcterms:creator
        ands:isOwnedBy
        ands:isManagedBy
        dcterms:abstract
        vivo:hasSubjectArea
        dcterms:keywords
        trel:hasSector
        ands:isOutputOf
        ) ;
    .

:ItemDescriptionFieldSet a z3c:PropertyGroup ;
    rdfs:label "Description" ;
    fresnel:group :DefaultGroup ;
    fresnel:showProperties (
        dcterms:spatial # geographic extent 
        dcterms:temporal # temporal extent 
        ) ;
    .

:ItemRelatedContentFieldSet a z3c:PropertyGroup ;
    rdfs:label "Related Content" ;
    rdfs:comment "title or explanatory caption" ;
    fresnel:group :DefaultGroup ;
    fresnel:showProperties (
        #[ fresnel:property ands:relatedInformationResource ;
        #  rdf:type fresnel:PropertyDescription ;
        #  fresnel:sublens :RelatedInformationLens ;
        #]
        ) ;
    .

:ItemAttributionFieldSet a z3c:PropertyGroup ;
    rdfs:label "Attribution" ;
    rdfs:comment "title or explanatory caption" ;
    fresnel:group :DefaultGroup ;
    fresnel:showProperties (
        dcterms:license # cc:license
        ) ;
    .
     

:OtherPropertyFieldSet a z3c:PropertyGroup ;
    rdfs:label "Other" ;
    rdfs:comment "Additional information not defined in other groups" ;
    fresnel:group :DefaultGroup ;
    fresnel:showProperties (
       fresnel:allProperties                                  
       );
    .




z3c:PropertyGroup a owl:Class ;
    rdfs:label "Property Group" ;
    rdfs:comment "Used to group properties. Allows to attach group label, and visual separation form other properties." ;
    rdfs:subClassOf fresnel:Lens ; # TODO: use something bette. sublass from Lens so that we can use fresnel:showProperties list.
    rdfs:isDefinedBy <http://namespaces.zope.org/z3c/form#> ;
    .

z3c:propertyGroup a owl:ObjectProperty ;
    rdfs:label "property group" ;
    rdfs:comment "property group to use. see fresnel:sublens" ;
    rdfs:isDefinedBy <http://namespaces.zope.org/z3c/form#> ;
    rdfs:domain fresnel:PropertyGroup ;  # maybe this should be a PropertyDescription?
    rdfs:range z3c:PropertyGroup ;
    .

z3c:field a owl:ObjectProperty ;
    rdfs:label "field" ;
    rdfs:comment "zope field type to use for editing / display in z3c.forms" ;
    rdfs:isDefinedBy <http://namespaces.zope.org/z3c/form#> ;
    rdfs:domain fresnel:Format ;
    rdfs:range z3c:Field ;
    .

z3c:fieldName a owl:DataProperty ;
    rdfs:label "field name" ;
    rdfs:comment "the field name (factory, class name) to instantiate this field" ;
    rdfs:isDefinedBy <http://namespaces.zope.org/z3c/form#> ;
    rdfs:Domain z3c:Field ;
    rdfs:range xsd:string ; # dottedname
    .

z3c:fieldDescription a owl:DataProperty ;
    rdfs:label "field description" ;
    rdfs:comment "a short description or help text to show along the field" ;
    rdfs:isDefinedBy <http://namespaces.zope.org/z3c/form#> ;
    rdfs:Domain z3c:Field ;
    rdfs:range xsd:string ;
    .

z3c:valueType a owl:DataProperty ;
    rdfs:label "value filed name" ;
    rdfs:comment "the field name for multi valued fields." ;
    rdfs:isDefinedBy <http://namespaces.zope.org/z3c/form#> ;
    rdfs:Domain z3c:Field ;
    rdfs:range xsd:string ; # dottedname
    .

z3c:valueClass a owl:ObjectProperty ;
    rdfs:label "Value Class" ;
    rdfs:comment "Used to query instances of this class, to generate vocabularies." ;
    rdfs:isDefinedBy <http://namespaces.zope.org/z3c/form#> ;
    rdfs:Domain z3c:Field ;
    .

# TODO: investigate this property here.
#       we usually define zope.schema.Field's here, but the widgetFactory
#       is applied to z3c.form.field.Field's, which are bound to the form
#       and can't be done here. maybe move this to the lens?
z3c:widgetFactory a owl:DataProperty ;
    rdfs:label "Widget name" ;
    rdfs:comment "factory for name for a specific widget to use. (python dotted name)." ;
    rdfs:isDefinedBy <http://namespaces.zope.org/z3c/form#> ;
    rdfs:Domain z3c:Field ;
    rdfs:range xsd:string ; # dottedname
    .

z3c:vocabulary a owl:ObjectProperty ;
    rdfs:label "Vocabuly" ;
    rdfs:comment "Vocabulary to use for allowed values. " ;
    rdfs:isDefinedBy <http://namespaces.zope.org/z3c/form#> ;
    rdfs:Domain z3c:Field ;
    .

z3c:query a owl:DataProperty ;
    rdfs:label "Vocabulary query" ;
    rdfs:isDefinedBy <http://namespaces.zope.org/z3c/form#> ;
    rdfs:Domain z3c:Vocabulary ;
    rdfs:range xsd:string ; # the query returning value, title, token
    .

z3c:Vocabulary a owl:Class ;
    rdfs:label "A Sparql driven Vocabulary" ;
    rdfs:isDefinedBy <http://namespaces.zope.org/z3c/form#> ;
    .

z3c:Field a owl:Class ;
    rdfs:label "Field" ;
    rdfs:comment "class to describe zope schema fields" ;
    rdfs:isDefinedBy <http://namespaces.zope.org/z3c/form#> ;
    .



z3c:TextLine a z3c:Field ;
    z3c:fieldName "gu.z3cform.rdf.schema.RDFLiteralLineField" ;
#    z3c:fieldType "" ; # define datatype for field if necessary ... could derive from property
#    z3c:defaultlang "" ; # default language ... works only with untyped fields ... strings?
#   other field properties:
#    min, max, length, required, widget (field.widgetfactory), ...
    .

z3c:Text a z3c:Field ;
    z3c:fieldName "gu.z3cform.rdf.schema.RDFLiteralField" ;
    .

z3c:MultiTextLine a z3c:Field ;
    z3c:fieldName "gu.z3cform.rdf.schema.RDFMultiValueField" ;
    z3c:valueType "gu.z3cform.rdf.schema.RDFLiteralLineField" ;
    .

z3c:MultiClassChoice a z3c:Field ;
    z3c:fieldName "gu.z3cform.rdf.schema.RDFMultiValueField" ;
    z3c:valueType "gu.z3cform.rdf.schema.RDFGroupedURIChoiceField" ;
    z3c:vocabulary z3c:RdfTypeVocabulary ;
    .

z3c:ImageChoice a z3c:Field ;
    z3c:fieldName "gu.z3cform.rdf.schema.RDFURIChoiceField" ;
    z3c:vocabulary z3c:ImageVocabulary ;
    .

z3c:GroupChoice a z3c:Field ;
    z3c:fieldName "gu.z3cform.rdf.schema.RDFURIChoiceField" ;
    z3c:vocabulary z3c:GroupVocabulary ;
    .

z3c:ResearchDataChoice a z3c:Field ;
    z3c:fieldName "gu.z3cform.rdf.schema.RDFURIChoiceField" ;
    z3c:vocabulary z3c:ResearchDataVocabulary ;
    .

z3c:ActivityChoice a z3c:Field ;
    z3c:fieldName "gu.z3cform.rdf.schema.RDFURIChoiceField" ;
    z3c:vocabulary z3c:ActivityVocabulary ;
    .

z3c:AddressChoice a z3c:Field ;
    z3c:fieldName "gu.z3cform.rdf.schema.RDFURIChoiceField" ;
    z3c:vocabulary z3c:AddressVocabulary ;
    .

z3c:MultiSectorChoice a z3c:Field ;
    z3c:fieldName "gu.z3cform.rdf.schema.RDFMultiValueField" ;
    z3c:valueType "gu.z3cform.rdf.schema.RDFURIChoiceField" ;
    z3c:vocabulary z3c:SectorVocabulary ;
    .

z3c:MultiDocumentTypeChoice a z3c:Field ;
    z3c:fieldName "gu.z3cform.rdf.schema.RDFMultiValueField" ;
    z3c:valueType "gu.z3cform.rdf.schema.RDFURIChoiceField" ;
    z3c:vocabulary z3c:DocumentTypeVocabulary ;
    .

z3c:MultiFORChoice a z3c:Field ;
    z3c:fieldName "gu.z3cform.rdf.schema.RDFMultiValueField" ;
    z3c:valueType "gu.z3cform.rdf.schema.RDFURIChoiceField" ;
    z3c:vocabulary z3c:FORVocabulary ;
    .

z3c:Date a z3c:Field ;
    z3c:fieldName "gu.z3cform.rdf.schema.RDFDateField" ;
    .

z3c:DateRange a z3c:Field ;
    z3c:fieldName "gu.z3cform.rdf.schema.RDFDateRangeField" ;
    .

z3c:RdfTypeVocabulary a z3c:Vocabulary ;
    z3c:valueClass owl:Class ;
    .

z3c:ImageVocabulary a z3c:Vocabulary ;
    z3c:valueClass foaf:Image ;
    .

z3c:GroupVocabulary a z3c:Vocabulary ;
    z3c:valueClass foaf:Group ;
    .

z3c:ResearchDataVocabulary a z3c:Vocabulary ;
    z3c:valueClass ands:ResearchData ;
    .

z3c:ActivityVocabulary a z3c:Vocabulary ;
    z3c:valueClass ands:Activity ;
    .

z3c:AddressVocabulary a z3c:Vocabulary ;
    z3c:valueClass ands:Address ;
    .

z3c:SectorVocabulary a z3c:Vocabulary ;
    z3c:valueClass tsec:Sector ;
    .

z3c:DocumentTypeVocabulary a z3c:Vocabulary ;
    z3c:valueClass ttyp:DocumentType ;
    .

# FIXME: would be a nice option for hierarchical vocab.
#        for now let people choose 6 digit codes.
# TODO: make title field selectable? (or just use z3c:query)
z3c:FORVocabulary a z3c:Vocabulary ;
    z3c:valueClass for08:FOR6 ;
    .

############# DC Elements


:dctitleFormat a fresnel:Format ;
    fresnel:propertyFormatDomain dc:title ;
    fresnel:label "Title (dc)" ;
    z3c:field z3c:TextLine ;
    fresnel:group :DefaultGroup ;
    .

:dcdescriptionFormat a fresnel:Format ;
    fresnel:propertyFormatDomain dc:description ;
    fresnel:label "Description (dc)" ;
    z3c:field z3c:Text ;
    fresnel:group :DefaultGroup ;
    .



############## DCTerms

:dctermstitleFormat a fresnel:Format ;
    fresnel:propertyFormatDomain dcterms:title ;
    fresnel:label "Title" ;
    z3c:field z3c:TextLine ;
    fresnel:group :DefaultGroup ;
    .

:dctermsdescriptionFormat a fresnel:Format ;
    fresnel:propertyFormatDomain dcterms:description ;
    fresnel:label "Description" ;
    z3c:field z3c:Text ;
    fresnel:group :DefaultGroup ;
    .

:dctermsidentifierFormat a fresnel:Format ;
    fresnel:propertyFormatDomain dcterms:identifier ;
    fresnel:label "Identifier" ;
    z3c:field z3c:TextLine ;
    fresnel:group :DefaultGroup ;
    .

:dctermstypeFormat a fresnel:Format ;
    fresnel:propertyFormatDomain dcterms:type;
    fresnel:label "Type" ;
    z3c:field z3c:TextLine ;
    fresnel:group :DefaultGroup ;
    .

:dctermscreatorFormat a fresnel:Format ;
    fresnel:propertyFormatDomain dcterms:creator;
    fresnel:label "Creator" ;
    z3c:field z3c:TextLine ;
    fresnel:group :DefaultGroup ;
   .

:dctermsspatialFormat a fresnel:Format ;
    fresnel:propertyFormatDomain dcterms:spatial;
    fresnel:label "Geographic extent polygon" ;
    z3c:field z3c:TextLine ;
    # TODO: fails on traversal ... 
    # Expression: <PythonExpr (context.restrictedTraverse('@@geosettings-view'))>
    # - Names:
    #   {'args': (),
    #    'context': <Graph identifier=http://terranova.org.au/ccaih/a14e415390cb4e17b0fc88dc6a699b46 (<class 'ordf.graph.Graph'>)>,
    #    'default': <object object at 0x1002c3b30>,
    #    'loop': {},
    #    'nothing': None,
    #    'options': {},
    #    'repeat': {},
    #    'request': <HTTPRequest, URL=http://localhost:8499/CCAIH/repository/gu-repository-content-repositoryitem-2/edit_metadata>,
    #    'template': <zope.browserpage.viewpagetemplatefile.ViewPageTemplateFile object at 0x109797210>,
    #    'view': <MapWidget 'form.widgets.http://purl.org/dc/terms/spatial'>,
    #    'views': <zope.browserpage.viewpagetemplatefile.ViewMapper object at 0x10cfb1390>}
    # Module zope.tales.pythonexpr, line 59, in __call__
    # - __traceback_info__: (context.restrictedTraverse('@@geosettings-view'))
    # Module <string>, line 1, in <module>
    #    AttributeError: 'Graph' object has no attribute 'restrictedTraverse'
    z3c:widgetFactory "collective.z3cform.mapwidget.widget.MapFieldWidget" ;
    fresnel:group :DefaultGroup ;
    .

:dctermskeywordFormat a fresnel:Format ;
    fresnel:propertyFormatDomain dcterms:keyword;
    fresnel:label "Keywords" ;
    z3c:field z3c:MultiTextLine ;
    fresnel:group :DefaultGroup ;
    .

:dctermsissuedFormat a fresnel:Format ;
    fresnel:propertyFormatDomain dcterms:issued;
    fresnel:label "Publication date" ;
    z3c:field z3c:TextLine ;
    fresnel:group :DefaultGroup ;
    .

:dctermstemporalFormat a fresnel:Format ;
    fresnel:propertyFormatDomain dcterms:temporal;
    fresnel:label "Temporal coverage" ;
    z3c:field z3c:DateRange ;
    #z3c:widgetFactory "collective.z3cform.datetimewidget.DateFieldWidget" ;
    #z3c:widgetFactory "gu.plone.rdf.widget.DateFieldWidget" ;

    fresnel:group :DefaultGroup ;
    .

:dctermsformatFormat a fresnel:Format ;
    fresnel:propertyFormatDomain dcterms:format;
    fresnel:label "Data format" ;
    z3c:field z3c:TextLine ;
    fresnel:group :DefaultGroup ;
    .

:dctermsrightsFormat a fresnel:Format ;
    fresnel:propertyFormatDomain dcterms:rights;
    fresnel:label "Rights" ;
    z3c:field z3c:MultiTextLine ;
    fresnel:group :DefaultGroup ;
    .

:dctermsprovenanceFormat a fresnel:Format ;
    fresnel:propertyFormatDomain dcterms:provenance;
    fresnel:label "Lineage" ;
    z3c:field z3c:MultiTextLine ;
    fresnel:group :DefaultGroup ;
    .

:dctermsbibliographicCitationFormat a fresnel:Format ;
    fresnel:propertyFormatDomain dcterms:bibliographicCitation;
    fresnel:label "Citation" ;
    z3c:field z3c:MultiTextLine ;
    fresnel:group :DefaultGroup ;
    .

:dctermsContributor a fresnel:Format ;
    fresnel:propertyFormatDomain dcterms:contributor ;
    fresnel:label "Author(s)" ;
    z3c:field z3c:MultiTextLine ;
    fresnel:group :DefaultGroup ;
    .

:rdfslabelFormat a fresnel:Format ;
    fresnel:propertyFormatDomain rdfs:label ;
    fresnel:label "Label" ;
    z3c:field z3c:MultiTextLine ;
    fresnel:group :DefaultGroup ;
    .

:rdftypeFormat a fresnel:Format ;
    fresnel:propertyFormatDomain rdf:type ;
    fresnel:label "Type" ;
    z3c:field z3c:MultiClassChoice ;
    #z3c:widgetFactory "z3c.formwidget.query.widget.QuerySourceFieldRadioWidget" ;
    #z3c:widgetFactory "z3c.formwidget.query.widget.QuerySourceFieldCheckboxWidget" ;
    z3c:widgetFactory "gu.z3cform.rdf.widgets.widget.GroupedSelectFieldWidget" ; # TODO: shouldn't this be the default widget for this sort of field?
    fresnel:group :DefaultGroup ;
    .

:dctermsabstractFormat a fresnel:Format ;
    fresnel:propertyFormatDomain dcterms:abstract;
    fresnel:label "Abstract" ;
    z3c:field z3c:MultiTextLine ;
    fresnel:group :DefaultGroup ;
    .

################### VIVO Fields
:vivoaddress1 a fresnel:Format ;
    fresnel:propertyFormatDomain vivo:address1;
    fresnel:label "Address Line 1" ;
    z3c:field z3c:TextLine ;
    fresnel:group :DefaultGroup .

:vivoaddress2 a fresnel:Format ;
    fresnel:propertyFormatDomain vivo:address2;
    fresnel:label "Address Line 2" ;
    z3c:field z3c:TextLine ;
    fresnel:group :DefaultGroup .

:vivoaddress3 a fresnel:Format ;
    fresnel:propertyFormatDomain vivo:address3;
    fresnel:label "Address Line 3" ;
    z3c:field z3c:TextLine ;
    fresnel:group :DefaultGroup .

:vivoaddressCityFormat a fresnel:Format ;
    fresnel:propertyFormatDomain vivo:addressCity;
    fresnel:label "City" ;
    z3c:field z3c:TextLine ;
    fresnel:group :DefaultGroup .

:vivoaddressStateFormat a fresnel:Format ;
    fresnel:propertyFormatDomain vivo:addressState;
    fresnel:label "State" ;
    z3c:field z3c:TextLine ;
    fresnel:group :DefaultGroup .

:vivoaddressCountryFormat a fresnel:Format ;
    fresnel:propertyFormatDomain vivo:addressCountry;
    fresnel:label "Country" ;
    z3c:field z3c:TextLine ;
    fresnel:group :DefaultGroup .

:vivoaddressPostalCodeFormat a fresnel:Format ;
    fresnel:propertyFormatDomain vivo:addressPostalCode;
    fresnel:label "Post code" ;
    z3c:field z3c:TextLine ;
    fresnel:group :DefaultGroup .

:vivophoneNumberFormat a fresnel:Format ;
    fresnel:propertyFormatDomain vivo:phoneNumber;
    fresnel:label "Telephone" ;
    z3c:field z3c:TextLine ;
    fresnel:group :DefaultGroup .

:vivoemailFormat a fresnel:Format ;
    fresnel:propertyFormatDomain vivo:email;
    fresnel:label "Email" ;
    z3c:field z3c:TextLine ;
    fresnel:group :DefaultGroup ; .

:vivohasSubjectAreaFormat a fresnel:Format ;
    fresnel:propertyFormatDomain vivo:hasSubjectArea;
    fresnel:label "FOR codes" ;
    z3c:field z3c:MultiFORChoice ;
    #z3c:widgetFactory "collective.z3cform.chosen.ChosenMultiFieldWidget" ;
    z3c:widgetFactory "collective.z3cform.chosen.AjaxChosenMultiFieldWidget" ;
    fresnel:group :DefaultGroup ; 
    .

################### BIBO Fields

:bibodoiFormat a fresnel:Format ;
    fresnel:propertyFormatDomain bibo:doi;
    fresnel:label "DOI" ;
    z3c:field z3c:TextLine ;
    fresnel:group :DefaultGroup ; 
    .

:bibouriFormat a fresnel:Format ;
    fresnel:propertyFormatDomain bibo:uri;
    fresnel:label "URI" ;
    z3c:field z3c:TextLine ;
    fresnel:group :DefaultGroup ; 
    .

:biboisbnFormat a fresnel:Format ;
    fresnel:propertyFormatDomain bibo:isbn;
    fresnel:label "ISBN" ;
    z3c:field z3c:TextLine ;
    fresnel:group :DefaultGroup ; 
    .

:biboissnFormat a fresnel:Format ;
    fresnel:propertyFormatDomain bibo:issn;
    fresnel:label "ISSN" ;
    z3c:field z3c:TextLine ;
    fresnel:group :DefaultGroup ; 
    .



################### FOAF Fields

:foafgivenNameFormat a fresnel:Format ;
    fresnel:propertyFormatDomain foaf:givenName ;
    fresnel:label "Given name" ;
    z3c:field z3c:TextLine ;
    fresnel:group :DefaultGroup ;
    .

:foaffamilyNameFormat a fresnel:Format ;
    fresnel:propertyFormatDomain foaf:familyName ;
    fresnel:label "Family name" ;
    z3c:field z3c:TextLine ;
    fresnel:group :DefaultGroup .

:foaforganisationFormat a fresnel:Format ;
    fresnel:propertyFormatDomain foaf:organisation ;
    fresnel:label "Organisation" ;
    z3c:field z3c:TextLine ;
    fresnel:group :DefaultGroup .

:foaftitleFormat a fresnel:Format ;
    fresnel:propertyFormatDomain foaf:title ;
    fresnel:label "Title" ;
    z3c:field z3c:TextLine ;
    fresnel:group :DefaultGroup .

:foafimg a fresnel:Format ;
    fresnel:propertyFormatDomain foaf:img ;
    fresnel:label "Image" ;
    z3c:field z3c:ImageChoice ;
    fresnel:group :DefaultGroup ;
    .

#################### ANDS Fields

:andsnla a fresnel:Format ;
    fresnel:propertyFormatDomain ands:nla ;
    fresnel:label "NLA Identifier" ;
    z3c:field z3c:TextLine ;
    fresnel:group :DefaultGroup ;
    .

:andsisMemberOf a fresnel:Format ;
    fresnel:propertyFormatDomain ands:isMemberOf ;
    fresnel:label "Member of" ;
    z3c:field z3c:GroupChoice ;
    fresnel:group :DefaultGroup ;
    .

:andsisCollectorOf a fresnel:Format ;
    fresnel:propertyFormatDomain ands:isCollectorOf ;
    fresnel:label "Collector of" ;
    z3c:field z3c:ResearchDataChoice ;
    fresnel:group :DefaultGroup ;
    .

:andsisOwnerOf a fresnel:Format ;
    fresnel:propertyFormatDomain ands:isOwnerOf ;
    fresnel:label "Owner of" ;
    z3c:field z3c:ResearchDataChoice ;
    fresnel:group :DefaultGroup ;
    .

:andsenriches a fresnel:Format ;
    fresnel:propertyFormatDomain ands:enriches ;
    fresnel:label "Enriches" ;
    z3c:field z3c:ResearchDataChoice ;
    fresnel:group :DefaultGroup ;
    .

:andsisParticipantIn a fresnel:Format ;
    fresnel:propertyFormatDomain ands:isParticipantIn ;
    fresnel:label "Participant in" ;
    z3c:field z3c:ActivityChoice ;
    fresnel:group :DefaultGroup ;
    .

:andsisPointOfContactFor a fresnel:Format ;
    fresnel:propertyFormatDomain ands:isPointOfContactFor ;
    fresnel:label "Point of contact for" ;
    z3c:field z3c:ResearchDataChoice ;
    fresnel:group :DefaultGroup ;
    .

:andstreetAddress a fresnel:Format ;
    fresnel:propertyFormatDomain ands:streetAddress ;
    fresnel:label "Street address" ;
    z3c:field z3c:AddressChoice ;
    fresnel:group :DefaultGroup ;
    .

:andpostalAddress a fresnel:Format ;
    fresnel:propertyFormatDomain ands:postalAddress ;
    fresnel:label "Postal address" ;
    z3c:field z3c:AddressChoice ;
    fresnel:group :DefaultGroup ;
    .

##################### Terranova Fields

:trelHasSector a fresnel:Format ;
    fresnel:propertyFormatDomain trel:hasSector ;
    fresnel:label "Sector" ;
    z3c:field z3c:MultiSectorChoice ;
    fresnel:group :DefaultGroup ;
    .

:trelHasDocumentType a fresnel:Format ;
    fresnel:propertyFormatDomain trel:hasDocumentType ;
    fresnel:label "Document type" ;
    z3c:field z3c:MultiDocumentTypeChoice ;
    z3c:widgetFactory "collective.z3cform.chosen.ChosenMultiFieldWidget" ;
    #z3c:widgetFactory "collective.z3cform.chosen.AjaxChosenMultiFieldWidget" ;
    fresnel:group :DefaultGroup ;
    .

##################### Time Fields

:timeHasBeginningFormat a fresnel:Format ;
    fresnel:propertyFormatDomain time:hasBeginning ;
    fresnel:label "Start Date" ;
    z3c:field z3c:TextLine ;
    fresnel:group :DefaultGroup ;
    .

:timeHasEndFormat a fresnel:Format ;
    fresnel:propertyFormatDomain time:hasEnd ;
    fresnel:label "End Date" ;
    z3c:field z3c:TextLine ;
    fresnel:group :DefaultGroup ;
    .


##################### ResRepo

:dctermsLicense a fresnel:Format ;
    fresnel:propertyFormatDomain ands:isPointOfContactFor ;
    fresnel:label "End-User Permissions" ;
    z3c:field z3c:TextLine ;
    fresnel:group :DefaultGroup ;
    .
                           
"""

custom = """
@prefix :        <http://namespaces.gu.edu.au/z3cform/fresnel#> .
@prefix dc:      <http://purl.org/dc/elements/1.1/> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix cvocab:  <http://namespaces.griffith.edu.au/collection_vocab#> .
@prefix fresnel: <http://www.w3.org/2004/09/fresnel#> .
@prefix z3c:     <http://namespaces.zope.org/z3c/form#> .
@prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#> .
@prefix rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

:MyItemLens a fresnel:Lens ;
    rdfs:label "Item metadata" ;
    fresnel:sublens :ItemLens ;
    fresnel:classLensDomain cvocab:Item ;
    fresnel:group :DefaultGroup ;
    fresnel:hideProperties ( rdf:type ) ;
    fresnel:showProperties ( 
                             dcterms:creator
                           ) ;
    .

:dctermscreatorFormat a fresnel:Format ;
    fresnel:propertyFormatDomain dcterms:creator;
    fresnel:label "Creator" ;
    z3c:field z3c:TextLine ;
    fresnel:group :DefaultGroup ;
    .
                            
"""

class FresnelLensEditForm(form.SchemaEditForm):
    grok.context(INavigationRoot)
    
    schema = IFresnelLensEditForm
    template = ViewPageTemplateFile('lenseditor.pt')

    enable_form_tabbing = False

    @property
    def localGraph(self):
        rdftool = getUtility(IORDF)
        store = rdftool.getLocalStore()
        return ConjunctiveGraph(store)
        
    def getContent(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IRDFSettings, check=False)
        graph_uri = settings.fresnel_graph_uri
        
        graph = Graph(identifier=graph_uri)
        graph.parse(StringIO(master), format='n3')
        graph.parse(StringIO(custom), format='n3')

        return dict(
            lens=graph.serialize(format='n3')
        )

#        return dict(
#            lens=self.localGraph.serialize(format='turtle')
#        )

    def update(self):
        super(FresnelLensEditForm, self).update()
        lens = self.widgets['lens']
        lens.rows = 40
        lens.addClass('codemirror-turtle')

    def applyChanges(self, data):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IRDFSettings, check=False)
        graph_uri = settings.fresnel_graph_uri
        
        localGraph = self.localGraph
        graph = Graph(identifier=graph_uri)
        graph.parse(StringIO(data['lens']), format='turtle')
        localGraph.remove_context(graph)
        quads = ((s,p,o,graph) for (s,p,o) in graph.triples((None, None, None)))
        localGraph.addN(quads)

        rdftool = getUtility(IORDF)
        rdftool.clearCache()
