import torch

from catalyst.dl.meters.ppv_tpr_f1_meter import PrecisionRecallF1ScoreMeter, \
                                                precision, recall, f1score


def precision_recall_f1(tp, fp, fn):
    """
    Calculates precision, recall, and f1 score.
    Args:
        tp: number of true positives
        fp: number of false positives
        fn: number of false negatives
    Returns:
        precision value (0-1), recall_value (0-1), f1score (0-1)
    """
    precision_value = round(precision(tp, fp), 3)
    recall_value = round(recall(tp, fn), 3)
    f1_value = round(f1score(precision_value, recall_value), 3)
    return (precision_value, recall_value, f1_value)


def test_precision_recall_f1score():
    """
    Sanity checks for the `precision`, `recall`, `f1score` functions.
    """
    # case 1
    tp, fp, fn = (10, 0, 0)
    ppv, tpr, f1 = precision_recall_f1(tp, fp, fn)
    assert ppv == tpr == f1 == 1., \
        "No fp and fn means everything should be =1"

    # case 2
    tp, fp, fn = (0, 0, 0)
    ppv, tpr, f1 = precision_recall_f1(tp, fp, fn)
    assert ppv == tpr == f1 == 0, \
        "Epsilon should make sure that there's no ZeroDivisionError"

    # case 3
    tp, fp, fn = (10, 10, 10)
    ppv, tpr, f1 = precision_recall_f1(tp, fp, fn)
    assert ppv == tpr == 0.5, \
        "Example where ppv and tpr should be =0.5."


def create_dummy_tensors_single():
    """
    Binary: 1 actual, 1 predicted (tp: 1, fp: 0, fn: 0)
    """
    label = torch.tensor([1])
    pred = torch.tensor([1])
    return (label, pred)


def create_dummy_tensors_batched(batch_size=16):
    """
    Binary: 1 actual, 1 predicted (tp: 1, fp: 0, fn: 0)
    """
    label = torch.zeros((batch_size, 1))
    pred = torch.zeros((batch_size, 1))
    for i in range(batch_size):
        label[i] = torch.tensor([1])
        pred[i] = torch.tensor([1])
    return (label, pred)


def test_meter():
    """
    Tests:
        * .reset()
        * .add()
        * .value()
    """
    meter = PrecisionRecallF1ScoreMeter()
    # tests the .reset() method, which happens to be called in initialization
    for key in ["tp", "fp", "fn"]:
        assert meter.tp_fp_fn_counts[key] == 0, \
            "Counts should be initialized to 0."

    # testing .add() and .value() with tensors w/no batch size dim
    # SHOULD FAIL
    binary_y, binary_pred = create_dummy_tensors_single()
    try:
        meter.add(binary_pred, binary_y)
        raise Exception(".add() should not be able to work with tensors \
                        that do not have the batch size dimension")
    except AssertionError:
        pass

    # testing .add() and .value() with tensors w/the batch size dim
    meter.reset()
    batch_size = 16
    binary_y, binary_pred = create_dummy_tensors_batched(batch_size)
    meter.add(binary_pred, binary_y)
    counts_dict = meter.tp_fp_fn_counts
    assert counts_dict["tp"] == batch_size
    assert counts_dict["fp"] == 0 and counts_dict["fn"] == 0, \
        "There should be no fp and fn for this test case."
    ppv, tpr, f1 = meter.value()
    ppv, tpr, f1 = map(lambda x: round(x, 3), [ppv, tpr, f1])
    assert ppv == tpr == f1 == 1, \
        "No fp and fn means that all metrics should be =1."
