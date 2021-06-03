"""`StepImplementer` for the `report` step which builds and pushes and artifacts archive.

Step Configuration
------------------
Step configuration expected as input to this step.
Could come from:

  * static configuration
  * runtime configuration
  * previous step results

Configuration Key           | Required? | Default | Description
----------------------------|-----------|---------|-------------
`organization`              | True      |         | Organization that this workflow is for. \
                                                    Used in archive name.
`application-name`          | True      |         | Application that this workflow is for. \
                                                    Used in archive name.
`service-name`              | True      |         | Service that this workflow is for. \
                                                    Used in archive name.
`version`                   | True      |         | Version of applicaiton service that this \
                                                    workflow is for. \
                                                    Used in archive name.
`archive-format`            | True      | 'zip'   | Archive format to use. For valid values see \
                                https://docs.python.org/3/library/shutil.html#shutil.make_archive
`archive-ignored-artifacts` | False     | `['package-artifacts', 'image-tar-file']` | \
    Result artifacts to not include in this this result artifacts archive.

Result Artifacts
----------------
Results artifacts output by this step.

Result Artifact Key        | Description
---------------------------|------------
`result-artifacts-archive` | local path to the generated results artifacts archive.

"""

import json
import os
import pprint
import shutil

from ploigos_step_runner import StepImplementer, StepResult

DEFAULT_CONFIG = {
    'archive-format': 'zip',
    'archive-ignored-artifacts': [
        'package-artifacts',
        'image-tar-file'
    ]
}

REQUIRED_CONFIG_OR_PREVIOUS_STEP_RESULT_ARTIFACT_KEYS = [
    'organization',
    'application-name',
    'service-name',
    'version',
    'archive-format'
]
class ResultArtifactsArchive(StepImplementer):
    """`StepImplementer` for the `report` step which builds and pushes and artifacts archive.
    """

    @staticmethod
    def step_implementer_config_defaults():
        """Getter for the StepImplementer's configuration defaults.

        Notes
        -----
        These are the lowest precedence configuration values.

        Returns
        -------
        dict
            Default values to use for step configuration values.
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

        results_artifacts_archive = self.__create_archive()

        if results_artifacts_archive:
            results_artifacts_archive_value = results_artifacts_archive
        else:
            results_artifacts_archive_value = 'No result artifact values to archive.'

        step_result.add_artifact(
            name='result-artifacts-archive',
            value=results_artifacts_archive_value,
            description='Archive of all of the step result artifacts marked for archiving.'
        )

        return step_result

    def __create_archive(self): # pylint: disable=too-many-branches,too-many-locals
        """Create the results artifact archive.

        Returns
        -------
        str
            Path to the created archive.
        """
        org = self.get_value('organization')
        app = self.get_value('application-name')
        service = self.get_value('service-name')
        version = self.get_value('version')
        result_archive_name = f"{org}-{app}-{service}-{version}"
        results_archive_root_dir_path = self.create_working_dir_sub_dir()

        ignored_artifacts = self.get_value('archive-ignored-artifacts')
        for previous_step_result in self.workflow_result.workflow_list:
            artifacts = previous_step_result.artifacts
            for artifact in artifacts.values():
                # only archive artifacts not on the ignore list
                if artifact.name not in ignored_artifacts:

                    # if value is path then copy the file(s) at path to archive location
                    # else create file with contents of value
                    if isinstance(artifact.value, str) and os.path.exists(artifact.value):
                        # create directory with name of artifact to put file(s) in
                        if previous_step_result.environment:
                            results_archvie_artifact_dir_path = self.create_working_dir_sub_dir(
                                os.path.join(
                                    result_archive_name,
                                    previous_step_result.step_name,
                                    previous_step_result.sub_step_name,
                                    previous_step_result.environment,
                                    artifact.name
                                )
                            )
                        else:
                            results_archvie_artifact_dir_path = self.create_working_dir_sub_dir(
                                os.path.join(
                                    result_archive_name,
                                    previous_step_result.step_name,
                                    previous_step_result.sub_step_name,
                                    artifact.name
                                )
                            )

                        if os.path.isfile(artifact.value):
                            shutil.copy(artifact.value, results_archvie_artifact_dir_path)
                        elif os.path.isdir(artifact.value):
                            dest_path = os.path.join(
                                results_archvie_artifact_dir_path,
                                os.path.basename(artifact.value)
                            )
                            shutil.copytree(artifact.value, dest_path)
                    else:
                        # create directory for step to put file with name of artifact in
                        if previous_step_result.environment:
                            results_archive_sub_step_dir_path = self.create_working_dir_sub_dir(
                                os.path.join(
                                    result_archive_name,
                                    previous_step_result.step_name,
                                    previous_step_result.sub_step_name,
                                    previous_step_result.environment
                                )
                            )
                        else:
                            results_archive_sub_step_dir_path = self.create_working_dir_sub_dir(
                                os.path.join(
                                    result_archive_name,
                                    previous_step_result.step_name,
                                    previous_step_result.sub_step_name
                                )
                            )
                        results_archive_artifact_file_path = os.path.join(
                            results_archive_sub_step_dir_path,
                            artifact.name
                        )

                        with open(results_archive_artifact_file_path, 'w') \
                                as results_archive_artifact_file:
                            # format the data to print to file based on its type
                            if isinstance(artifact.value, str):
                                formated_artifact_value = artifact.value
                            elif isinstance(artifact.value, (dict, list)):
                                formated_artifact_value = json.dumps(
                                    artifact.value,
                                    indent=4
                                )
                            else:
                                printer = pprint.PrettyPrinter()
                                formated_artifact_value = printer.pformat(artifact.value)

                            # write data to file
                            results_archive_artifact_file.write(formated_artifact_value)

        # make the archive if there was anyting to archive
        archive_base_name = os.path.join(results_archive_root_dir_path, result_archive_name)
        if os.path.exists(archive_base_name):
            results_artifacts_archive = shutil.make_archive(
                base_name=archive_base_name,
                format=self.get_value('archive-format'),
                root_dir=results_archive_root_dir_path,
                base_dir=result_archive_name
            )
        else:
            results_artifacts_archive = None

        return results_artifacts_archive
