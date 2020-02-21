from typing import List, Dict, Optional, Type

DEFAULT_EMPTY = "_"


class ProcessorPrototype:
    tasks: List[str]
    empty_value: str

    def __init__(self, empty_value: Optional[str] = None):
        """ Applies postprocessing. Simplest Processor one could use.

        :param empty_value: Value to use to fill tasks that would not get any data


        >>> x = ProcessorPrototype(empty_value="%")
        >>> x.set_tasks(["a", "b"])
        >>> x.reinsert("x") == {"form": "x", "a": "%", "b": "%"}
        True
        >>> x.get_dict("y", ["1", "2"]) == {"form": "y", "a": "1", "b": "2"}
        True
        """
        self.tasks = []
        self.empty_value = empty_value or DEFAULT_EMPTY

    def set_tasks(self, tasks):
        self.tasks = tasks

    def postprocess(self, line):
        pass

    def reinsert(self, form: str) -> Dict[str, str]:
        """ Generates an automatic line for a token that was removed from lemmatization

        :param form: Token to reinsert
        :return: Dictionary representation of the token, as an annotation


        >>> x = ProcessorPrototype(empty_value="%")
        >>> x.set_tasks(["a", "b"])
        >>> x.reinsert("x") == {"form": "x", "a": "%", "b": "%"}
        True
        """
        return dict(form=form, **{task: self.empty_value for task in self.tasks})

    def get_dict(self, token: str, tags: List[str]) -> Dict[str, str]:
        """ Get the dictionary representation of a token annotation

        :param token: Token used as input for pie
        :param tags: List of tags generated
        :return: Dictionary representation of the token and its annotations

        >>> x = ProcessorPrototype(empty_value="%")
        >>> x.set_tasks(["a", "b"])
        >>> x.get_dict("y", ["1", "2"]) == {"form": "y", "a": "1", "b": "2"}
        True
        """
        return {"form": token, **{k: val for k, val in zip(self.tasks, tags)}}

    def reset(self):
        """ Functions that should be run in between documents

        >>> x = ProcessorPrototype(empty_value="%")
        >>> x.set_tasks(["a", "b"])
        >>> x.reset()
        """
        pass


class RenamedTaskProcessor(ProcessorPrototype):
    MAP: Dict[str, str] = {}

    def __init__(self, **kwargs):
        """ This Processor is used for renaming tasks (Pie for example refuses tasks containing dots)

        >>> class ExampleRemaped(RenamedTaskProcessor):
        ...    MAP = {"task_name_1": "renamed"}
        >>> x = ExampleRemaped()
        >>> x.set_tasks(["task_name_1", "y"])
        >>> x.get_dict("token", ["a", "b"]) == {"form": "token", "renamed": "a", "y": "b"}
        True
        """
        super(RenamedTaskProcessor, self).__init__(**kwargs)
        self._map: Dict[str, str] = type(self).MAP

    def set_tasks(self, tasks):
        self.tasks = [self._map.get(task, task) for task in tasks]


class ChainedProcessor(ProcessorPrototype):
    """ Allows for easy chaining !

    The ChainedProcessor is basically using its headprocessor in the background and checking it's output to some extent

    The prototype of ChainedProcessor using Processor Prototype would have the same results because
    chained processor is not doing anything new except enabling chaining

        >>> x = ProcessorPrototype(empty_value="%")
        >>> x.set_tasks(["a", "b"])
        >>> y = ChainedProcessor(x)
        >>> y.set_tasks(["a", "b"])
        >>> x.reinsert("x") == y.reinsert("x")
        True
        >>> x.get_dict("y", ["1", "2"]) == y.get_dict("y", ["1", "2"])
        True

    You can subclass it to modify the output of the preceding processor :

    >>> class ExampleChained(ChainedProcessor):
    ...     def reinsert(self, form: str) -> Dict[str, str]:
    ...         annotation = self.head_processor.reinsert(form)
    ...         annotation["col3"] = "x"
    ...         return annotation
    ...
    ...     def get_dict(self, form: str, tags: List[str]) -> Dict[str, str]:
    ...         annotation = self.head_processor.get_dict(form, tags)
    ...         annotation["col3"] = "x"
    ...         return annotation
    ...
    >>> x = ExampleChained(ProcessorPrototype(empty_value="EMPTY"))
    >>> x.set_tasks(["a", "b"])
    >>> x.reinsert("x") == {"form": "x", "a": "EMPTY", "b": "EMPTY", "col3": "x"}
    True
    >>> x.get_dict("y", ["1", "2"]) == {"form": "y", "a": "1", "b": "2", "col3": "x"}
    True

    """
    head_processor: ProcessorPrototype

    def __init__(self, head_processor: Optional[ProcessorPrototype], **kwargs):
        super(ChainedProcessor, self).__init__(**kwargs)

        self.head_processor: ProcessorPrototype = head_processor
        if not self.head_processor:
            self.head_processor = ProcessorPrototype()

    def set_tasks(self, tasks):
        super(ChainedProcessor, self).set_tasks(tasks)
        self.head_processor.set_tasks(tasks)

    def reinsert(self, form: str) -> Dict[str, str]:
        return self.head_processor.reinsert(form)

    def get_dict(self, token: str, tags: List[str]) -> Dict[str, str]:
        return self.head_processor.get_dict(token, tags)

    def reset(self):
        self.head_processor.reset()
