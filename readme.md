# Custom workouts for Garmin Watch

1. Define your workouts in a `.yaml` file with the following format:

    ```yaml
    workouts:
    - name: LEG DAY
        steps:
        - name: Squats
            series: 4
            reps: 10
        - name: Deadlift
            series: 3
            reps: 8-10
            notes: last set AMRAP
    ```

    Check `example.yaml` for more examples.

2. Run the script:

    ```sh
    python workout.py path/to/workout.yaml
    ```

3. Connect your Garmin Watch through USB, and copy the generated `.fit` files to `<garmin watch>/Internal Storage/GARMIN/NewFiles`.

4. Done. Workouts should show up.

## Notes

I made this to fit my needs, so there's some hardcoded behavior that works for me but might not work for you:

* The script creates strength workouts. This could be expanded easily.
* There's a hardcoded 1m rest between sets, and 3m rest between exercises. This could be expanded easily.
* Exercises are not recognized by the Garmin Connect app. Meaning you won't see the trained muscle groups or any other details. This could be supported, but not so easily.