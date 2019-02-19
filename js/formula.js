function linear_interpolate(x, x_0, x_1, y_0, y_1) {
    let m = (y_1 - y_0) / x_1 - x_0;
    let c = y_0;
    let y = (m * x) + c;
    return y;
}
function S(x, max, mid, stp) {
    let arg = -(stp * (x - mid));
    let y = max / (1 + Math.exp(arg));
    return y;
}
function gain(start, end) {
    if (end < start) {
        // treat negative gain as no gain
        return 0;
    }
    else {
        return end - start;
    }
}
MAX_A = 1.2
MAX_B = 1.7
MAX_C = 7
function max(start) {
    return MAX_A + MAX_B / ((start / MAX_C) + 1);
}
MID_A = 20
MID_B = 500
MID_M = 25000
function mid(start) {
    let sig_mp_0 = MID_A;
    let sig_mp_1 = MID_B;
    return linear_interpolate(start, 0, MID_M, sig_mp_0, sig_mp_1);
}
STEEP_A = 0.05
STEEP_C = 100
function stp(start) {
    return STEEP_A / ((start / STEEP_C) + 1);
}
function C(start, end) {
    return S(gain(start, end), max(start), mid(start), stp(start));
}

function update_params() {
    window.MAX_A = parseFloat(document.getElementsByName('max_a')[0].value);
    window.MAX_B = parseFloat(document.getElementsByName('max_b')[0].value);
    window.MAX_C = parseFloat(document.getElementsByName('max_c')[0].value);
    window.MID_A = parseFloat(document.getElementsByName('mid_a')[0].value);
    window.MID_B = parseFloat(document.getElementsByName('mid_a')[0].value);
    window.MID_M = parseFloat(document.getElementsByName('mid_m')[0].value);
    window.STEEP_A = parseFloat(document.getElementsByName('steep_a')[0].value);
    window.STEEP_C = parseFloat(document.getElementsByName('steep_b')[0].value);
}

function plot_data(evt) {
    if (evt) {
        evt.preventDefault();
    }    update_params();
    //var  = [...Array(5).keys()];
    const startings = [1, 5, 10, 20, 50];
    let series = [];
    for (let starting of startings) {
        let serie = []
        for (let i = starting; i < 100; i++) {
            serie.push([i, C(starting, i)]);
        }
        series.push({
            name: '' + starting,
            data: serie
        })
    }

    Highcharts.chart('container', {
        chart: {
            type: 'line'
        },
        title: {
            text: 'Rendimenti'
        },
        series: series
    });
    return false;
}
document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('main-form').addEventListener('submit', plot_data);
});