# Analyzers
from elasticsearch_dsl import analyzer


class Analyzers:
    exact_analyzer = analyzer(
        'exact_analyzer', tokenizer='keyword', filter=["lowercase", "asciifolding"],
    )

    acronym_analyzer = analyzer(
        'acronym_analyzer', tokenizer='pattern', filter=["lowercase"], pattern="(\\w+\\.)"
    )

    almost_exactly_analyzer = analyzer(
        'almost_exactly_analyzer', tokenizer='standard', filter=["lowercase", "asciifolding"]
    )

    whitespace_mistake_analyzer = analyzer(
        'whitespace_mistake_analyzer', tokenizer='whitespace', filter=["lowercase"]
    )

    standard_analyzer = analyzer(
        'match_analyzer', tokenizer='standard'
    )

    mistake_analyzer = analyzer(
        'mistake_analyzer', tokenizer='standard', filter=["lowercase", "asciifolding", "spellcheck"]
    )

    url_analyzer = analyzer(
        'url_analyzer', tokenizer='uax_url_email', filter=["lowercase", "stop"]
    )
