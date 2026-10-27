"""Excellent fits must still leave observations visually identifiable."""
from matplotlib.figure import Figure
from tpd_spectra.workflow_analysis import draw_result


def test_observations_use_markers_and_fitted_curve_has_contrasting_style():
    figure=Figure()
    draw_result(figure,dict(snapshot={'method':'Polanyi–Wigner'},values={},plots={
        'x':[100,101,102], 'observed':[1,2,1], 'predicted':[1,2,1],
        'x_label':'Temperature (°C)', 'y_label':'Signal'}))
    observed,fitted=figure.axes[0].lines
    assert observed.get_marker()=='o'
    assert observed.get_markerfacecolor()=='white'
    assert observed.get_color()!=fitted.get_color()
    assert fitted.get_linewidth()>observed.get_linewidth()
    assert figure.axes[1].get_ylabel()=='Residual'
