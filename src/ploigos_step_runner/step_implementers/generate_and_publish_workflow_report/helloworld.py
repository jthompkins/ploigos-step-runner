"""`StepImplementer` for the `generate-metadata` step using Git.
Step Configuration
------------------
Step configuration expected as input to this step.
Could come from:
  * static configuration
  * runtime configuration
  * previous step results
Configuration Key     | Required? | Default | Description
----------------------|-----------|---------|-----------
TODO

Result Artifacts
----------------
Results artifacts output by this step.
Result Artifact Key | Description
--------------------|------------
TODO

"""


from ploigos_step_runner import StepImplementer, StepResult

DEFAULT_CONFIG = {
   TODO
}

REQUIRED_CONFIG_OR_PREVIOUS_STEP_RESULT_ARTIFACT_KEYS = [
   TODO
]

class HelloWorld(StepImplementer):  
    """StepImplementer for the generate-and-publish-workflow-report step for HelloWorld.
    """

    @staticmethod
    def step_implementer_config_defaults():
        """Getter for the StepImplementer's configuration defaults.
        Returns
        -------
        dict
            Default values to use for step configuration values.
        Notes
        -----
        These are the lowest precedence configuration values.
        """
        return DEFAULT_CONFIG

    @staticmethod
    def _required_config_or_result_keys():
        """Getter for step configuration or previous step result artifacts that are required before
        running this step.
        See Also
        --------
        _validate_required_config_or_previous_step_result_artifact_keys
        Returns
        -------
        array_list
            Array of configuration keys or previous step result artifacts
            that are required before running the step.
        """
        return REQUIRED_CONFIG_OR_PREVIOUS_STEP_RESULT_ARTIFACT_KEYS

    def _run_step(self):
        """Runs the step implemented by this StepImplementer.
        Returns
        -------
        StepResult
            Object containing the dictionary results of this step.
        """
        step_result = StepResult.from_step_implementer(self)
	TODO - Add Logic Here
        return step_result

