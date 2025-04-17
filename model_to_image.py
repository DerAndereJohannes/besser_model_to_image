from graphviz import Digraph
from typing import Dict
from besser.BUML.metamodel.structural import DomainModel, Class, Property, \
     Multiplicity, BinaryAssociation, StringType, IntegerType, DateType, \
     Generalization, Enumeration, EnumerationLiteral, Method, Parameter, DateTimeType



VISIBILITY_MAP = {
        'public': '+',
        'private': '-',
        'protected': '#',
        'package': '~'
}

def model_to_image(model: DomainModel, layout_engine: str = 'neato', file_format: str = 'png', view: bool = False):
    # Initialize the graph
    dot = Digraph(comment=f'{model.name}',
                  engine=layout_engine,
                  graph_attr={'nodesep': '1',
                              'ranksep': '1'},
                  node_attr={'shape': 'record'},
                  edge_attr={'len': '3',
                             'labelfontsize': '16',
                             # 'labeldistance': '3'
                             })

    # Handle Classes, Properties and Methods
    for cls in model.get_classes():
        if cls.is_abstract:
            node_label = f'{{«abstract»\\n{cls.name}|'
        else:
            node_label = f'{{{cls.name}|'

        # Add Properties
        for prop in cls.attributes:
            node_label += f'{VISIBILITY_MAP[prop.visibility]} {prop.name} : {prop.type.name}\\l'

        if cls.methods and cls.attributes:
            node_label += '|'
        # Add Methods
        for method in cls.methods:
            node_label += handle_mathod_label(method, cls.is_abstract)

        node_label += '}'

        dot.node(cls.name, label=node_label)

    # Handle Enumerations
    for e in model.get_enumerations():
        node_label = f'{{«enumeration»\\n{e.name}|'

        for literal in e.literals:
            node_label += f'{literal.name}\\l'

        node_label += '}'

        dot.node(e.name, label=node_label)

    # Handle Generalizations
    for g in model.generalizations:
        dot.edge(g.specific.name, g.general.name,
                 arrowhead='empty',
                 len='2.5')

    # Handle Associations
    for a in model.associations:
        source, sink = a.ends
        arrow_head = 'none'

        if not source.is_navigable or not sink.is_navigable:
            arrow_head = 'open'

            # Reverse if is_navigable is false for a point
            if not sink.is_navigable:
                source, sink = sink, source
        elif source.is_composite or sink.is_composite:
            arrow_head = 'diamond'
            if sink.is_composite:
                source, sink = sink, source

        dot.edge(source.type.name, sink.type.name,
                 arrowhead=arrow_head,
                 taillabel=f'{source.name} {handle_multiplicity_label(source.multiplicity)}',
                 headlabel=f'{sink.name} {handle_multiplicity_label(sink.multiplicity)}')

    # Handle Rendering
    dot.render(model.name, format=file_format, view=view)

def handle_multiplicity_label(multiplicity: Multiplicity, asterisk_value: int = 9999) -> str:
    # Convert asterisk value to an asterisk
    min_value = multiplicity.min if multiplicity.min != asterisk_value else '*'
    max_value = multiplicity.max if multiplicity.max != asterisk_value else '*'

    if multiplicity.min == multiplicity.max:
        return f'({min_value})'
    else:
        return f'({min_value}...{max_value})'

def handle_mathod_label(method: Method, cls_is_abstract: bool) -> str:
    # f'{VISIBILITY_MAP[method.visibility]} {method.name}() : {method.type}\\l'

    output_type = 'void' if not method.type else method.type.name
    method_label = f'{VISIBILITY_MAP[method.visibility]} {method.name}('

    for param in method.parameters:
        method_label += f'{param.name}: {param.type.name}'

    method_label += f'): {output_type}'

    if method.is_abstract and cls_is_abstract:
        method_label += '«abstract»'

    method_label += '\\l'

    return method_label

if __name__ == '__main__':

    # Genre Enumeration
    book_genre: Enumeration = Enumeration(
            name='Genre',
            literals={
                EnumerationLiteral(name='Fantasy'),
                EnumerationLiteral(name='SciFi'),
                EnumerationLiteral(name='Adventure'),
                EnumerationLiteral(name='Mystery'),
                EnumerationLiteral(name='History'),
                EnumerationLiteral(name='Philosophy'),
            }
    )

    # Library example from the documentation https://besser.readthedocs.io/en/latest/buml_language/model_building/buml_core.html
    # Library attributes definition
    library_name: Property = Property(name='name', type=StringType)
    address: Property = Property(name='address', type=StringType)

    # Library class definition
    library: Class = Class(name='Library', attributes={library_name, address})

    # Book attributes definition
    title: Property = Property(name='title', type=StringType)
    pages: Property = Property(name='pages', type=IntegerType)
    release: Property = Property(name='release', type=DateType)
    genre: Property = Property(name='genre', type=book_genre)

    # Book class definition
    book: Class = Class(name='Book', attributes={title, pages, release, genre})

    # Author attributes definition
    author_name: Property = Property(name='name', type=StringType)
    email: Property = Property(name='email', type=StringType)

    # Author class definition
    author: Class = Class(name='Author', attributes={author_name, email})

    # Library-Book association definition
    located_in: Property = Property(name='locatedIn', type=library, multiplicity=Multiplicity(1, 1))
    has: Property = Property(name='has', type=book, multiplicity=Multiplicity(0, '*'))
    lib_book_association: BinaryAssociation = BinaryAssociation(name='lib_book_assoc', ends={located_in, has})

    # Book-Author association definition
    publishes: Property = Property(name='publishes', type=book, multiplicity=Multiplicity(0, '*'))
    written_by: Property = Property(name='writtenBy', type=author, multiplicity=Multiplicity(1, '*'))
    book_author_association: BinaryAssociation = BinaryAssociation(name='book_author_assoc', ends={written_by, publishes})

    # Generalizations fiction, non-fiction
    fiction = Class(name='Fiction')
    nonfiction = Class(name='Non-Fiction')
    gen_fiction_book: Generalization = Generalization(general=book, specific=fiction)
    gen_nonfiction_book: Generalization = Generalization(general=book, specific=nonfiction)

    # Generalizations book format
    ebook = Class(name='Ebook')
    hardcover = Class(name='Hardcover')
    gen_ebook_book: Generalization = Generalization(general=book, specific=ebook)
    gen_hardcover_book: Generalization = Generalization(general=book, specific=hardcover)

    # Loan system example
    member: Class = Class(name='Member', is_abstract=True)
    loan: Class = Class(name='Loan')
    student: Class = Class(name='Student')
    others: Class = Class(name='Others')

    gen_student_member: Generalization = Generalization(general=member, specific=student)
    gen_others_member: Generalization = Generalization(general=member, specific=others)

    # Loan attributes definition
    public: Property = Property(name='public', type=StringType)
    private: Property = Property(name='private', type=DateTimeType, visibility='private')
    protected: Property = Property(name='protected', type=IntegerType, visibility='protected')
    package: Property = Property(name='package', type=IntegerType, visibility='package')

    loan.attributes = {public, private, protected, package}


    # Uni-direction example
    loan_books: Property = Property(name='loans', type=book, multiplicity=Multiplicity(0, '*'))
    on_loan: Property = Property(name='onLoan', type=loan, multiplicity=Multiplicity(1, 1), is_navigable=False)
    book_loan_association: BinaryAssociation = BinaryAssociation(name='book_loan_assoc', ends={loan_books, on_loan})

    # Composite example
    loaned_by: Property = Property(name='loan_owner', type=member, multiplicity=Multiplicity(0, '*'))
    holds_loan: Property = Property(name='holds_loan', type=loan, multiplicity=Multiplicity(1, 1), is_composite=True)
    loan_member_association: BinaryAssociation = BinaryAssociation(name='loan_member_assoc', ends={loaned_by, holds_loan})

    # method example
    member_get_name: Method = Method(name='getName', type=StringType)
    member_calculate_something: Method = Method(name='calculateSth', parameters={Parameter(name='sth', type=StringType)}, type=IntegerType, visibility='private', is_abstract=True)
    member_protected: Method = Method(name='protect', parameters={Parameter(name='sth', type=DateType)}, visibility='protected')
    member_package: Method = Method(name='package', visibility='package')

    member.methods = {member_get_name, member_calculate_something, member_protected, member_package}

    student.methods = {member_calculate_something}
    others.methods = {member_calculate_something}

    # Domain model definition
    library_model: DomainModel = DomainModel(
            name='Library_model', types={library, book, author, book_genre, loan, member, student, others},
            associations={lib_book_association, book_author_association, book_loan_association, loan_member_association},
            generalizations={gen_fiction_book, gen_nonfiction_book, gen_ebook_book, gen_hardcover_book, gen_student_member, gen_others_member},
    )

    model_to_image(library_model, layout_engine='dot', view=True)

