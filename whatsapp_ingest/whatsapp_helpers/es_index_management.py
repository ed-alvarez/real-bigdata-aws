from elasticsearch_dsl import Document, connections


class manageESIndex:
    def __init__(self):
        self._template_name = str()
        self._index_pattern = str()
        self._dsl_document = Document()
        self._data_input_alias = str()
        self._move_data = False
        self._update_input_alias = True
        self._es = None

    @property
    def templateName(self):
        return self._template_name

    @templateName.setter
    def templateName(self, value):
        self._template_name = value

    @property
    def indexPattern(self):
        return self._index_pattern

    @indexPattern.setter
    def indexPattern(self, value):
        self._index_pattern = value

    @property
    def dslDocument(self):
        return self._dsl_document

    @dslDocument.setter
    def dslDocument(self, value):
        self._dsl_document = value

    @property
    def dataInputAlias(self):
        return self._data_input_alias

    @dataInputAlias.setter
    def dataInputAlias(self, value):
        self._data_input_alias = value

    @property
    def moveData(self):
        return self._move_data

    @moveData.setter
    def moveData(self, value):
        self._move_data = value

    @property
    def updateInputAlias(self):
        return self._update_input_alias

    @updateInputAlias.setter
    def updateInputAlias(self, value):
        self._update_input_alias = value

    def template(self):
        """Create an IndexTemplate and save it into elasticsearch."""
        index_template = self._dsl_document._index.as_template(template_name=self._template_name, pattern=self._index_pattern)
        index_template.save()

        self.create_and_migrate()

        return

    def create_and_migrate(self, _index_id=1):
        """
        Upgrade function that creates a new index for the data. Optionally it also can
        (and by default will) reindex previous copy of the data into the new index
        (specify ``move_data=False`` to skip this step) and update the alias to
        point to the latest index (set ``update_alias=False`` to skip).
        Note that while this function is running the application can still perform
        any and all searches without any loss of functionality. It should, however,
        not perform any writes at this time as those might be lost.
        """

        # get the low level connection
        self._es = connections.get_connection()

        # Get the largest Index number that exists and add one to it for the new index
        _es_last_index = 0
        _previous_index = ""
        for index in self._es.indices.get(self._index_pattern):
            _index_number = int(index.split("-")[-1])
            if _index_number >= _es_last_index:
                _previous_index = index
                _es_last_index = _index_number

        _index_id = _es_last_index + 1
        _index_number = str(_index_id).zfill(6)

        # construct a new index name by appending current timestamp
        _next_index = self._index_pattern.replace("*", _index_number)

        # create new index, it will use the settings from the template
        self._es.indices.create(index=_next_index)

        if self._move_data:
            # move data from current alias to the new index
            self._es.reindex(
                body={"source": {"index": _previous_index}, "dest": {"index": _next_index}},
                request_timeout=3600,
            )
            # refresh the index to make the changes visible
            self._es.indices.refresh(index=_next_index)

        if self._update_input_alias and self._data_input_alias and _previous_index:
            # repoint the data input alias to point to the newly created index
            self._es.indices.update_aliases(
                body={
                    "actions": [
                        {"remove": {"alias": self._data_input_alias, "index": _previous_index}},
                        {"add": {"alias": self._data_input_alias, "index": _next_index}},
                    ]
                }
            )
        elif self._update_input_alias and self._data_input_alias and not _previous_index:
            self._es.indices.update_aliases(
                body={
                    "actions": [
                        {"add": {"alias": self._data_input_alias, "index": _next_index}},
                    ]
                }
            )

        return
