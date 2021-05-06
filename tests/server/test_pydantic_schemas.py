from speedo_common.api_schemas import PostSubmission


def test_fixture_syncro_with_pydantic(make_submission_dict):
    api_create_submission = make_submission_dict(nb_tags=4)
    submission = PostSubmission(**api_create_submission)
    assert submission.dict().keys() == api_create_submission.keys()
