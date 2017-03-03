def date_to_solr_format(datetime_object):
    """
    http://lucene.apache.org/solr/4_4_0/solr-core/org/apache/solr/schema/DateField.html
    :param datetime_object:
    :return: datetime as string in solr format. Ex: 1995-12-31T23:59:59Z
    """
    return datetime_object.isoformat()
