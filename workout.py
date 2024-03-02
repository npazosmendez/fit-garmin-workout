from fit_tool.fit_file_builder import FitFileBuilder
from fit_tool.profile.messages.file_id_message import FileIdMessage
from fit_tool.profile.messages.workout_message import WorkoutMessage
from fit_tool.profile.messages.workout_step_message import WorkoutStepMessage
from fit_tool.profile.messages.exercise_title_message import ExerciseTitleMessage
from fit_tool.profile.profile_type import Sport, SubSport, Intensity, WorkoutStepDuration, WorkoutStepTarget, Manufacturer, FileType
import datetime
from random import randint
import yaml
from sys import argv

class Workout:
    def __init__(self, name):
        self.name = name
        self.exercises = {}
        self.step_index = 0
        self.title_index = 0
        self.steps = []
        self.titles = []

    def write(self, filename):
        file_id_message = FileIdMessage()
        file_id_message.type = FileType.WORKOUT
        file_id_message.manufacturer = Manufacturer.GARMIN.value
        file_id_message.product = 65534
        file_id_message.serial_number = randint(0, 0xFFFFFFFF)
        file_id_message.time_created = round(datetime.datetime.now().timestamp() * 1000)

        workout_message = WorkoutMessage()
        workout_message.sport = Sport.TRAINING
        workout_message.capabilities = 32
        workout_message.num_valid_steps = len(self.steps)
        workout_message.workout_name = self.name
        workout_message.sub_sport = SubSport.STRENGTH_TRAINING

        builder = FitFileBuilder(auto_define=True, min_string_size=50)
        builder.add(file_id_message)
        builder.add(workout_message)
        for step in self.steps:
            builder.add(step)

        for title in self.titles:
            builder.add(title)

        fit_file = builder.build()
        fit_file.to_file(filename)
        print(f"Encoded FIT file {filename}")

    def add_workout_step(self, name, series, reps, notes=''):
        step = {
            'name': name,
            'series': series,
            'duration_type': WorkoutStepDuration.REPS,
            'duration_value': 0,
            'target_type': WorkoutStepTarget.OPEN,
            'target_value': 0,
            'notes': notes,
            'category': 0,  # ExerciseCategory.Row is not defined in fit_tool
        }

        try:
            step['duration_value'] = int(reps)
            step['duration_type'] = WorkoutStepDuration.REPS
        except ValueError:
            step['name'] = name + ' (' + reps + ')'
            step['notes'] = reps + '\n' + step['notes']

        self.add_workout_step_with_params(step)

    def add_workout_step_with_params(self, step):
        if len(self.steps) > 0:
            # Additional 2m rest between exercises, total of 3m
            rest = WorkoutStepMessage()
            rest.message_index = self.step_index
            self.step_index += 1
            rest.duration_type = WorkoutStepDuration.TIME
            rest.duration_value = 60000 * 2
            rest.target_type = WorkoutStepTarget.OPEN
            rest.target_value = 0
            rest.intensity = Intensity.REST
            self.steps.append(rest)

        workout_step_mesg = WorkoutStepMessage()
        workout_step_mesg.message_index = self.step_index
        self.step_index += 1

        workout_step_mesg.duration_type = step['duration_type']
        if 'duration_value' in step:
            workout_step_mesg.duration_value = step['duration_value']
        if step['notes']:
            workout_step_mesg.notes = step['notes']

        workout_step_mesg.target_type = step['target_type']
        workout_step_mesg.target_value = step['target_value']
        workout_step_mesg.intensity = Intensity.ACTIVE
        workout_step_mesg.exercise_category = step['category']
        workout_step_mesg.weight_display_unit = 1

        exercise_id = self.exercises.get(step['name'])
        if exercise_id is None:
            exercise_id = len(self.exercises)
            self.exercises[step['name']] = exercise_id
            title = ExerciseTitleMessage()
            title.message_index = self.title_index
            self.title_index += 1
            title.exercise_name = exercise_id
            title.exercise_category = step['category']
            title.workout_step_name = step['name']
            self.titles.append(title)

        workout_step_mesg.exercise_name = exercise_id
        workout_step_mesg.repeat_steps = 4
        self.steps.append(workout_step_mesg)

        if step['series'] > 0:
            # 1m rest between series
            rest = WorkoutStepMessage()
            rest.message_index = self.step_index
            self.step_index += 1
            rest.duration_type = WorkoutStepDuration.TIME
            rest.duration_value = 60000
            rest.target_type = WorkoutStepTarget.OPEN
            rest.target_value = 0
            rest.intensity = Intensity.REST
            self.steps.append(rest)

            repeat = WorkoutStepMessage()
            repeat.message_index = self.step_index
            self.step_index += 1
            repeat.duration_type = WorkoutStepDuration.REPEAT_UNTIL_STEPS_CMPLT
            repeat.duration_value = workout_step_mesg.message_index
            repeat.target_value = step['series']
            self.steps.append(repeat)



if __name__ == "__main__":
    with open(argv[1], 'r') as file:
        data = yaml.safe_load(file)
    for workout in data['workouts']:
        w = Workout(workout['name'])
        for step in workout['steps']:
            w.add_workout_step(step['name'], step['series'], step['reps'], step.get('notes', ''))
        w.write(workout['name']+ '.fit')


