
class Themes:
    """
    A class used to represent different themes for plotting.

    Attributes
    ----------
    A4Large : dict
        A dictionary containing settings for a large A4 plot.
    A4Medium : dict
        A dictionary containing settings for a medium A4 plot.
    A4Small : dict
        A dictionary containing settings for a small A4 plot.
    A4Slim : dict
        A dictionary containing settings for a slim A4 plot.
    A4Mini : dict
        A dictionary containing settings for a mini A4 plot.
    """

    A4Large = {"xNumbers": 12, "yNumbers":10, "zNumbers":10, "marker.tickLength":50, "marker.tickWidth":4,  "height":3000, "width":5000, "fontSize":146}
    A4Medium = {"xNumbers": 10, "yNumbers":8, "zNumbers":8, "marker.tickLength":50, "marker.tickWidth":4,  "height":3000, "width":4000, "fontSize":132}
    A4Small = {"xNumbers": 8, "yNumbers":8, "zNumbers":6, "marker.tickLength":50, "marker.tickWidth":4,  "height":2000, "width":3000, "fontSize":128}
    A4Slim = {"xNumbers": 10, "yNumbers":6, "zNumbers":6, "marker.tickLength":50, "marker.tickWidth":4, "height":1300, "width":4000, "fontSize":128}
    A4Mini = {"xNumbers": 6, "yNumbers":5, "zNumbers":5, "marker.tickLength":50, "marker.tickWidth":4, "height":2000, "width":2500, "fontSize":112}
