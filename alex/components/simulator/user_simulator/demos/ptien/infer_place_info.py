from alex.utils.config import as_project_path
from alex.components.dm.ontology import Ontology
from alex.utils.sample_distribution import sample_from_list
import copy
import pdb

def add_place_info(goal):
    infer = InferInfo()
    final_goal = infer.infer_info(goal)
    if final_goal != goal:
        print '***---Goal is added info....'
        print '---Original goal', goal
        print '---Final goal:', final_goal
        #pdb.set_trace()
    return final_goal

class InferInfo(object):

    def __init__(self):
        path = as_project_path('applications/PublicTransportInfoEN/data/ontology.py')
        self.ontology = Ontology(path)

    def get_accepted_mpv(self, ds, slot, accepted_slots):
        if slot in self.goal.keys():
            return self.goal[slot]
        else:
            return 'none'

    def infer_info(self, goal):
        ds = None
        accepted_slots = None
        self.goal = copy.deepcopy(goal)
        #self.goal['abc'] = 'thanh le'

        # retrieve the slot variables
        from_city_val = self.get_accepted_mpv(ds, 'from_city', accepted_slots)
        from_borough_val = self.get_accepted_mpv(ds, 'from_borough', accepted_slots)
        from_stop_val = self.get_accepted_mpv(ds, 'from_stop', accepted_slots)
        from_street_val = self.get_accepted_mpv(ds, 'from_street', accepted_slots)
        from_street2_val = self.get_accepted_mpv(ds, 'from_street2', accepted_slots)
        to_city_val = self.get_accepted_mpv(ds, 'to_city', accepted_slots)
        to_borough_val = self.get_accepted_mpv(ds, 'to_borough', accepted_slots)
        to_stop_val = self.get_accepted_mpv(ds, 'to_stop', accepted_slots)
        to_street_val = self.get_accepted_mpv(ds, 'to_street', accepted_slots)
        to_street2_val = self.get_accepted_mpv(ds, 'to_street2', accepted_slots)
        vehicle_val = self.get_accepted_mpv(ds, 'vehicle', accepted_slots)
        max_transfers_val = self.get_accepted_mpv(ds, 'num_transfers', accepted_slots)

        # infer cities based on stops
        from_cities, to_cities = None, None
        stop_city_inferred = False
        if from_stop_val != 'none' and from_city_val == 'none':
            from_cities = self.ontology.get_compatible_vals('stop_city', from_stop_val)
            if len(from_cities) == 1:
                from_city_val = from_cities.pop()
                stop_city_inferred = True
            elif len(from_cities)>1:
                self.goal['from_city']= sample_from_list(from_cities)
        if to_stop_val != 'none' and to_city_val == 'none':
            to_cities = self.ontology.get_compatible_vals('stop_city', to_stop_val)
            if len(to_cities) == 1:
                to_city_val = to_cities.pop()
                stop_city_inferred = True
            elif len(from_cities)>1:
                self.goal['to_city']= sample_from_list(to_cities)
                
        # infer cities based on stops
        from_boroughs, to_boroughs = None, None
        stop_borough_inferred = False
        if from_stop_val != 'none' and from_borough_val == 'none':
            from_boroughs = self.ontology.get_compatible_vals('stop_borough', from_stop_val)
            if len(from_boroughs) == 1:
                from_borough_val = from_boroughs.pop()
                stop_borough_inferred = True
            elif len(from_boroughs)>1:
                self.goal['from_borough']= sample_from_list(from_boroughs)
        if to_stop_val != 'none' and to_borough_val == 'none':
            to_boroughs = self.ontology.get_compatible_vals('stop_borough', to_stop_val)
            if len(to_boroughs) == 1:
                to_borough_val = to_boroughs.pop()
                stop_borough_inferred = True
            elif len(to_boroughs)>1:
                self.goal['to_borough']= sample_from_list(to_boroughs)

        # infer boroughs based on streets
        from_boroughs_st, to_boroughs_st = None, None
        street_borough_inferred = False
        if to_street_val != 'none' and to_borough_val == 'none':
            to_boroughs_st = self.ontology.get_compatible_vals('street_borough', to_street_val)
            if len(to_boroughs_st) == 1:
                to_borough_val = to_boroughs_st.pop()
                street_borough_inferred = True
            elif len(to_boroughs_st)>1:
                self.goal['to_borough']= sample_from_list(to_boroughs_st)
        if from_street_val != 'none' and from_borough_val == 'none':
            from_boroughs_st = self.ontology.get_compatible_vals('street_borough', from_street_val)
            if len(from_boroughs_st) == 1:
                from_borough_val = from_boroughs_st.pop()
                street_borough_inferred = True
            elif len(from_boroughs_st)>1:
                self.goal['from_borough']= sample_from_list(from_boroughs_st)

        # infer cities based on each other
        if from_stop_val != 'none' and from_city_val == 'none' and to_city_val in from_cities:
            from_city_val = to_city_val
        elif to_stop_val != 'none' and to_city_val == 'none' and from_city_val in to_cities:
            to_city_val = from_city_val

        # infer boroughs based on each other
        # from stops
        if from_stop_val != 'none' and from_borough_val == 'none' and to_borough_val in from_boroughs:
            from_borough_val = to_borough_val
        elif to_stop_val != 'none' and to_borough_val == 'none' and from_borough_val in to_boroughs:
            to_borough_val = from_borough_val
        # from streets
        if from_street_val != 'none' and from_borough_val == 'none' and to_borough_val in from_boroughs_st:
            from_borough_val = to_borough_val
        elif to_street_val != 'none' and to_borough_val == 'none' and from_borough_val in to_boroughs_st:
            to_borough_val = from_borough_val

        # try to infer cities from intersection
        if to_cities is not None and from_cities is not None and from_city_val == 'none' and to_city_val == 'none':
            intersect_c = [c for c in from_cities if c in to_cities]
            if len(intersect_c) == 1:
                from_city_val = intersect_c.pop()
                to_city_val = from_city_val
                stop_city_inferred = True

        # try infer boroughs from intersection
        if to_boroughs is not None and from_boroughs is not None and from_borough_val == 'none' and to_borough_val == 'none':
            intersect_b = [b for b in from_boroughs if b in to_boroughs]
            if len(intersect_b) == 1:
                from_borough_val = intersect_b.pop()
                to_borough_val = from_borough_val
                stop_borough_inferred = True
        if to_boroughs_st is not None and from_boroughs_st is not None and from_borough_val == 'none' and to_borough_val == 'none':
            intersect_bs = [b for b in from_boroughs_st if b in to_boroughs_st]
            if len(intersect_bs) == 1:
                from_borough_val = intersect_bs.pop()
                to_borough_val = from_borough_val
                street_borough_inferred = True

        # place can be specified by street or stop and area by city or borough or another street
        has_from_place = from_stop_val != 'none' or from_street_val != 'none' or from_city_val not in ['none', 'New York']
        has_from_area = from_borough_val !='none' or from_street2_val != 'none' or from_city_val != 'none'
        from_info_complete = has_from_place and has_from_area

        has_to_place = to_stop_val != 'none' or to_street_val != 'none' or to_city_val not in ['none', 'New York']
        has_to_area = to_borough_val !='none' or to_street2_val != 'none' or to_city_val != 'none'

        # hack for from CITY to CITY and allowing New York as one of them
        if (has_to_area and has_from_area) and from_city_val != to_city_val:
            has_to_place = True
            has_from_place = True

        to_info_complete = has_to_place and has_to_area

        return self.goal
