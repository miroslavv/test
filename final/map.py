import xml.etree.ElementTree as ET
import math
from collections import defaultdict
import random



class Node:
    def __init__(self, elem):
       self.id=elem.attrib['id']
       self.lat=float(elem.attrib['lat'])
       self.lon=float(elem.attrib['lon'])
       self.ways=set()

    def __hash__(self):
        """
        hash aj equality ratame cisto na zaklade id. Dva nody sa teda rovnaju (==) pokial maju
        rovnake id. zaroven, nody (aj cesty) vieme vkladat do (hash) dictov a (hash) setov.
        """
        return self.id.__hash__()

    def __eq__(self, other):
        return self.id==other.id

    def __repr__(self):
        return "Node(id=%s, way=%s)"%(self.id, self.pretty_print_ways)

    def pretty_print_ways(self):
        res= ', '.join({way.name for way in self.ways if way.name!='unnamed'})
        return res if res else 'unnamed'

class Way:
    def __init__(self, elem):
       self.id=elem.attrib['id']
       try:
           self.name=elem.findall("./tag[@k='name']")[0].attrib['v']
       except Exception:
           self.name='unnamed'
       self.nodes=set()
       self.elem=elem

    def __hash__(self):
        return self.id.__hash__()

    def __eq__(self, other):
        return self.id==other.id

    def __repr__(self):
        return "Way(name=%s)"%self.name

def dist(node1, node2):
    return math.sqrt((node1.lat-node2.lat)**2+(node1.lon-node2.lon)**2)

def is_way(elem):
    """
    vrati True/False, podla toho, ci xml element `elem` popisuje cestu, ktora nas zaujima (teda
    napr. nie footway. Dalo by sa to nakodit aj krajsie, ale uz je to takto :)
    """
    motorways={'living_street', 'motorway_link', 'trunk', 'track', 'give_way', 'tertiary_link',
            'tertiary', 'motorway_junction', 'residential', 'secondary_link', 'service',
            'traffic_signals', 'trunk_link', 'primary', 'primary_link', 'raceway', 
            'motorway', 'crossing', 'secondary'}

    for child in elem.iter():
        if child.tag=='tag' and child.attrib.get('k',None)=='highway' and child.attrib.get('v',None) in motorways:
                return True
    return False

def graph_from_dict(graph_dict):
    """
    convenient metoda, ktora preraba graf z formatu, v ktorom ho vytvorime na format, v ktorom ho
    akceptuje funkcia dijkstra.
    `graph_dict` je dict, taky, ze graph_dict[vertex]={(sused1, vzd1), (sused2,vzd2)... }. Vrati
    funkciu graph, ktora robi to, ze ked sa zavola ako graph(vertext), vrati to iste ako
    graph_dict[vertex]
    """
    def graph(vertex):
        return graph_dict[vertex]
    return graph

def dijkstra(graph, ver_start, ver_end):
    """
    find optimal path between vertices ver_start and ver_end. `graph` is function, that accepts
    vertex and returns list (or other iterable) of (neighbour, distance) pairs. returns tuple (dist,
    path) where dist is optimal distance and path is sequence of vertices
    """
    #boundary and final have the following structure: {vertex: (distance, previous_vertex)} where
    #distance is the distance from node_start to vertex and previous_vertex is semi-last vertex on
    #the ver_start - vertext path optimal path.

    boundary={}
    final={}
    boundary[ver_start]=(0, None)
    while True:
        if not boundary:
            return None, None
        closest_ver, (closest_dist, prev_vertex) = min(boundary.items(), key=lambda item: item[1][0])
        final[closest_ver] = closest_dist, prev_vertex
        del boundary[closest_ver]
        for ver, dst in graph(closest_ver):
            if ver not in final:
                if ver not in boundary or boundary[ver][0]>closest_dist+dst:
                    boundary[ver]=(closest_dist+dst, closest_ver)
        if closest_ver == ver_end:
            break
    path=[ver_end]
    iterator=ver_end
    while not iterator == ver_start:
        iterator=final[iterator][1]
        path.append(iterator)

    return final[ver_end][0], path


if __name__=="__main__":
    tree = ET.parse('map.osm')
    way=tree.findall(".//way")[0]

    #mnozina so vsetkymi cestami, uz vo forme objektov! cesty cesty zatial maju empty way.nodes,
    #tieto bude treba doplnit neskor
    all_ways={Way(elem) for elem in tree.findall(".//way") if is_way(elem)}
    #to iste, ale s nodmi
    all_nodes={Node(elem) for elem in tree.findall(".//node")}
    #pomocny slovnik, aby sme vedeli superfast rychlo najst node pomocou jeho id-cka
    all_nodes_dict={node.id: node for node in all_nodes}

    #struktura, ktora bude popisovat nas graf: graph_dict[vertex] bude {(sused1, vzd1),
    #(sused2,vzd2)... } etc. aby sa nam lahsie kodilo, na zaciatok nainicializujeme graph_dict tak,
    #aby defaultna hodnota vo vsetkych novych vrcholoch bola empty set
    graph_dict=defaultdict(set)

    for way in all_ways:
        elem_nodes=list(way.elem.findall(".//nd"))
        #teraz vyuzijeme all_nodes_dict, z id-ciek zostrojime nody
        nodes = [all_nodes_dict[elem_node.attrib['ref']] for elem_node in elem_nodes]
        for node in nodes:
            #prelinkujeme navzajom node a way
            node.ways.add(way)
            way.nodes.add(node)
        #husty sposob, ako iterovat cez nodes tak, aby node1, node2 boli po sebe iduce nody
        for node1, node2 in zip(nodes, nodes[1:]):
            graph_dict[node1].add((node2, dist(node1, node2)))
            graph_dict[node2].add((node1, dist(node1, node2)))
                    
    #nechame si iba nody s neprazdnou mnozinou ways, nody mimo ciest nas nezaujimaju
    all_street_nodes=[node for node in all_nodes if node.ways]

    
    #hladame dovtedy, kym nenajdeme 2 body, ktore SU spojene.
    while True:
        graph=graph_from_dict(graph_dict)
        node1=random.choice(all_street_nodes)
        node2=random.choice(all_street_nodes)
        dist, path=dijkstra(graph, node1, node2)
        if dist: break

    #pretty print
    print('\n'.join("%s [%.3f %.3f]"%(node.pretty_print_ways(), node.lat, node.lon) for node in path))
    


