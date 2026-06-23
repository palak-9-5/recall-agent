def calculate_next_review(
    quality: int, 
    easiness: float, 
    repetitions: int, 
    interval: int
) -> tuple[int, float, int]:
    """Calculates the next review interval and easiness factor using the SuperMemo-2 (SM-2) algorithm.
    
    Parameters:
    - quality (int): The grade quality score from 0 to 5.
                     5: perfect response.
                     4: correct response with minor hesitation/omission.
                     3: correct response with significant difficulty/omissions.
                     2: incorrect response, but close/seemed easy to recall.
                     1: incorrect response, but recalled the concept name.
                     0: complete blackout/wrong.
    - easiness (float): The current easiness factor (EF) of the concept.
    - repetitions (int): Number of consecutive successful reviews (quality >= 3).
    - interval (int): The current interval in days between reviews.
    
    Returns:
    - tuple: (new_interval, new_easiness, new_repetitions)
             new_interval (int): number of days to wait until next review.
             new_easiness (float): updated easiness factor.
             new_repetitions (int): updated count of consecutive correct reviews.
    """
    # 1. Update repetitions and interval
    if quality >= 3:
        # Correct answer
        if repetitions == 0:
            new_interval = 1
        elif repetitions == 1:
            new_interval = 6
        else:
            new_interval = int(round(interval * easiness))
        new_repetitions = repetitions + 1
    else:
        # Incorrect answer: reset repetitions to 0, start over with interval of 1 day
        new_repetitions = 0
        new_interval = 1

    # 2. Update Easiness Factor (EF)
    # Formula: EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    new_easiness = easiness + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    
    # The SM-2 algorithm specifies that EF should never fall below 1.3
    if new_easiness < 1.3:
        new_easiness = 1.3
        
    return new_interval, new_easiness, new_repetitions
