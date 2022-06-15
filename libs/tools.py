from typing import Tuple, List
from osmnx.plot import plot_graph, _save_and_show

CUSTOM_FILTER = (
    '["highway"]["area"!~"yes"]["highway"!~"bridleway|bus_guideway|bus_stop|construction|cycleway|elevator|footway|'
    "motorway|motorway_junction|motorway_link|escalator|proposed|construction|platform|raceway|rest_area|"
    'path|service"]["access"!~"customers|no|private"]["public_transport"!~"platform"]'
    '["fee"!~"yes"]["foot"!~"no"]["service"!~"drive-through|driveway|parking_aisle"]["toll"!~"yes"]'
)


def get_route_length(graph, route) -> float:
    return sum([graph.get_edge_data(u, v)[0]["length"] for u, v in zip(route, route[1:] + [route[0]])]) / 1000.0


def get_longest_route(org_graph, cycles) -> Tuple[List, float]:
    longest_route = (list(), 0)
    for i, l in enumerate(cycles):
        if longest_route[1] < (length := get_route_length(org_graph, l)):
            longest_route = (l, length)
    return longest_route[0], longest_route[1]


def plot_graph_route(graph, route, route_color="r", route_linewidth=4, route_alpha=0.5, ax=None, **pg_kwargs):
    """Plot a route along a graph. Allowing routes for multigraphs (two edges for the same nodes)
    Args:
    graph (networkx.MultiDiGraph) input graph
    route (list): route as a list of triples (node1, node2, key of the edge)
    route_color (string) color of the route
    route_linewidth (int): width of the route line
    route_alpha (float): opacity of the route line
    orig_dest_size (int): size of the origin and destination nodes
    ax  (matplotlib axis): if not None, plot route on this preexisting axis instead of creating a new fig, ax
      and drawing the underlying graph
    pg_kwargs: keyword arguments to pass to plot_graph
    Returns
    fig, ax (tuple): matplotlib figure, axis
    """
    if ax is None:
        # plot the graph but not the route, and override any user show/close
        # args for now: we'll do that later
        override = {"show", "save", "close"}
        kwargs = {k: v for k, v in pg_kwargs.items() if k not in override}
        fig, ax = plot_graph(graph, show=False, save=False, close=False, **kwargs)
    else:
        fig = ax.figure

    # assemble the route edge geometries' x and y coords then plot the line
    x = [graph.nodes[route[0]]["x"]]
    y = [graph.nodes[route[0]]["y"]]

    for r in zip(route, route[1:] + [route[0]]):
        u, v = r
        data = graph.get_edge_data(v, u) or graph.get_edge_data(u, v)
        d = 0

        data = data[d]
        if "geometry" in data:
            # if geometry attribute exists, add all its coords to list
            xs, ys = data["geometry"].xy
            data["geometry"]

            # Revert the path if geometry is flipped
            if x[-1] != xs[0] or y[-1] != ys[0]:
                x.extend(xs[::-1])
                y.extend(ys[::-1])
            else:
                x.extend(xs)
                y.extend(ys)

        else:
            # otherwise, the edge is a straight line from node to node
            x.extend((graph.nodes[u]["x"], graph.nodes[v]["x"]))
            y.extend((graph.nodes[u]["y"], graph.nodes[v]["y"]))
    ax.plot(x, y, c=route_color, lw=route_linewidth, alpha=route_alpha)

    # save and show the figure as specified, passing relevant kwargs
    sas_kwargs = {"save", "show", "close", "filepath", "file_format", "dpi"}
    kwargs = {k: v for k, v in pg_kwargs.items() if k in sas_kwargs}
    fig, ax = _save_and_show(fig, ax, **kwargs)
    return fig, ax
