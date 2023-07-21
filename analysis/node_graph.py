import mesh_database_client
import networkx as nx
import os


class NYCMeshGraph:
    def __init__(self, links_df):
        links_df["weight"] = 1
        self.links_df = links_df

        self.graph = nx.MultiDiGraph()
        self.exit_nodes = [10, 713]

        self.update_graph()

    def update_graph(self):
        self.graph = nx.from_pandas_edgelist(self.links_df, "to", "from", ["weight"])

        # Get only the largest connected component
        largest_connected = max(
            nx.connected_components(self.graph.to_undirected()), key=len
        )
        self.graph = self.graph.subgraph(largest_connected).copy()

    def get_downstream_nodes(self, nn):
        distances, paths = nx.algorithms.multi_source_dijkstra(
            self.graph, self.exit_nodes
        )
        egress_forest = nx.DiGraph(
            (node_id, egress_path[-2])
            for node_id, egress_path in paths.items()
            if len(egress_path) > 1
        )

        return nx.ancestors(egress_forest, nn)

    def get_dependent_nodes(self, nn):
        downstream_nodes = self.get_downstream_nodes(nn)

        graph_during_outage = self.graph.copy()
        graph_during_outage.remove_node(nn)

        fully_dependent_nodes = set({})
        for node_id in downstream_nodes:
            component = nx.node_connected_component(
                graph_during_outage.to_undirected(), node_id
            )
            if all(n not in component for n in self.exit_nodes):
                fully_dependent_nodes.add(node_id)

        # partially_dependent_nodes = downstream_nodes - fully_dependent_nodes

        # alternate_paths = nx.algorithms.multi_source_dijkstra_path(
        #     graph_during_outage, self.exit_nodes
        # )
        return list(fully_dependent_nodes)


if __name__ == "__main__":
    spreadsheet_id = os.environ.get("SPREADSHEET_ID")
    database_client = mesh_database_client.DatabaseClient(
        spreadsheet_id=spreadsheet_id, include_active=True
    )

    links_df = database_client.active_link_df
    graph = NYCMeshGraph(links_df)
    dependent_nns = graph.get_dependent_nodes(1971)
    print(dependent_nns)
