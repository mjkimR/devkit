"""``RULE-steering-documents``, loaded by ``devkit rules`` from this synchronized copy.

The implementation is ``devkit_spec.features.governance.usecases.steering_documents`` in the installed devkit-spec package; the class
defined here is what ``devkit rules`` instantiates, and the guide beside this file is what ``devkit rules explain`` prints.
"""

from devkit_spec.features.governance.usecases.steering_documents import SteeringDocumentsRule as _Implementation


class SteeringDocumentsRule(_Implementation):
    """Steering documents stay flat, ID-free, summarized in English and within the count and size caps."""
