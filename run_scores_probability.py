from game_database import load_games


def get_outs(play):
    return play['count']['outs']

def get_runner_id(runner):
    return runner['details']['runner']['id']

def get_runner_end_base(runner):
    return runner['movement']['end']


def runner_scores_on_play(play, runner_id):
    for runner in get_runners(play):
        if get_runner_id(runner) == runner_id:
            if runner['movement']['isOut']:
                return False
            elif get_runner_end_base(runner) == 'score':
                return True
    return False


def runner_scores_in_inning(plays, curr_play_num, runner_id):
    while curr_play_num < len(plays):
        play = plays[curr_play_num]

        score_res = runner_scores_on_play(play, runner_id)
        if score_res:
            return True
        if get_outs(play) == 3:
            return False
        curr_play_num += 1



def get_runners(play):
    ids = {}
    for runner in play['runners']:
        ids[get_runner_id(runner)] = runner
    return ids.values()


def runner_scores_ratio(game, runner_predicate):
    scores = 0
    attempts = 0
    plays = game['liveData']['plays']['allPlays']

    for i, play in enumerate(plays):
        for runner in get_runners(play):
            if runner_predicate(play, runner):
                scores_run = runner_scores_in_inning(plays, i, get_runner_id(runner))
                if scores_run is not None:
                    scores += scores_run
                    attempts += 1

    return scores, attempts


def runner_scores_games_ratio(games, runner_predicate):
    scores = 0
    attempts = 0

    for game in games:
        curr_scores, curr_attempts = runner_scores_ratio(game, runner_predicate)
        scores += curr_scores
        attempts += curr_attempts

    return scores, attempts


def second_no_outs(play, runner):
    outs = get_outs(play)
    base = get_runner_end_base(runner)
    return outs == 0 and base == '2B'

def third_less_than_2_outs(play, runner):
    outs = get_outs(play)
    base = get_runner_end_base(runner)
    return outs < 2 and base == '3B'

def third_no_outs(play, runner):
    outs = get_outs(play)
    base = get_runner_end_base(runner)
    return outs == 0 and base == '3B'

def team_third_less_than_2_outs(is_away):
    return lambda play, runner: play['about']['isTopInning'] == is_away and third_less_than_2_outs(play, runner)


if __name__ == "__main__":
    scores, attempts = runner_scores_games_ratio(
        load_games("2025-02-19", "2025-04-19"),
        third_no_outs
    )
    print(f"{scores}/{attempts} : {scores / attempts * 100:.4f}%")
