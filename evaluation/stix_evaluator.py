from copy import deepcopy
import warnings

def format_floats(func):
    """
    Decorator for formatting floating numbers to 5 decimals.
    Args:
        func: A func that returns 3 float numbers and a dictionary of values being dictionaries containing floats
    Reurns:
        The func wrapped to return floats
    """
    def wrapper_of_floats(*args, **kwargs):
        precision, recall, f1, full_res = func(*args, **kwargs)
        precision = float("{:.5f}".format(round(precision, 5)))
        recall = float("{:.5f}".format(round(recall, 5)))
        f1 = float("{:.5f}".format(round(f1, 5)))
        for k, v in full_res.items():
            for key in v.keys():
                if type(full_res[k][key])==float:
                    full_res[k][key] = float("{:.5f}".format(round(full_res[k][key], 5)))
        return precision, recall, f1, full_res
    return wrapper_of_floats

class DifferentLenghtsError(Exception):
    """
    Exception raised for different length of prediction and actual lists.
    """

    def __init__(self, message, pred_len, actual_len):
        super().__init__()
        self.message = message
        self.pred_len = pred_len
        self.actual_len = actual_len

    def __str__(self):
        return f"{self.message}\nPredictions lenght: {self.pred_len}\nActual lenght: {self.actual_len}"
    
class STIXWarning(Warning):
    pass

class STIXEvaluator:

    def __init__(self, comparison_values:list=None, cti_object_types:list=None):
        """
        Create an instance of STIX evaluator.
        Args:
            comparison_values (list): List of attributes per object in stix bundle to use for evaluation.
                                      Default is ["type", "name"]
            cti_object_types (list): List of object types to use for evaluation. 
                                     Default is ['identity', 'report', 'relationship',
                                                 'indicator', 'file', 'malware', 
                                                 'attack-pattern', 'domain-name', 'intrusion-set', 
                                                 'url', 'vulnerability', 'location', 'hostname',
                                                 'cryptocurrency-wallet', 'email-addr', 'ipv4-addr']
        """

        if comparison_values==None:
            self.comparison_values = ["type", "name"]
            warnings.warn("\nType and Name will be used to compare stix objects!", STIXWarning)
        else:
            self.comparison_values = comparison_values
        
        if cti_object_types==None:
            self.cti_object_types = [
                'identity', 'report', 'relationship',
                'indicator', 'file', 'malware', 
                'attack-pattern', 'domain-name', 'intrusion-set', 
                'url', 'vulnerability', 'location', 'hostname',
                'cryptocurrency-wallet', 'email-addr', 'ipv4-addr'
            ]
            warnings.warn("\nAll cti types will be evaluated!", STIXWarning)
        else:
            self.cti_object_types = cti_object_types

        self.results_template = {
            "precision":0,
            "recall":0,
            "f1":0,
            "pred_count":0,
            "actual_count":0,
            "true_positives":0,
            "false_positives":0,
            "false_negatives":0,
            "weight":0,
            "agg_weight":1
            }

    def select_comparison_values(self, stix_bundle:dict) -> list:
        """
        Select the correct attributes for each stix object and filters irrelevant.
        Args:
            stix_bundle (dict): A stix bundle.
        Returns:
            object_attributes (list): A list of filtered objects and attributes in stix bundles.
        """

        object_attributes = []

        for obj in stix_bundle["objects"]:

            if obj["type"] not in self.cti_object_types:
                continue
            else:
                if "id" in self.comparison_values:
                    object_attributes.append((obj["type"], obj["id"]))
                elif "name" in obj.keys():
                    object_attributes.append((obj["type"], obj["name"]))
                elif "value" in obj.keys():
                    object_attributes.append((obj["type"], obj["value"]))
                elif "hashes" in obj.keys():
                    object_attributes.append((obj["type"], obj["hashes"]))
                elif "relationship_type" in obj.keys():
                    object_attributes.append((obj["type"], obj["relationship_type"], obj["source_ref"], obj["target_ref"]))
                else:
                    continue
        
        return object_attributes


    def bring_comparison_values(self, predicted:dict, actual:dict) -> list:
        """
        Bring the predicted and actual objects using a subset of their attributes for comparison.
        Args:
            predicted (dict): Predicted stix bundle.
            actual (dict): Actual stix bundle.
        Returns:
            predicted_objects (list), actual_objects (list): The lists of predicted and actual filtered objects in stix bundles.
        """

        if "type" not in self.comparison_values:
            raise ValueError("Type attribute can't be ommited in comparison_values.")
        
        if "name" not in self.comparison_values and "id" not in self.comparison_values:
            raise ValueError("Name or ID must be selected in comparison_values.")
        
        predicted_objects = self.select_comparison_values(predicted)
        actual_objects = self.select_comparison_values(actual)

        return predicted_objects, actual_objects

    @format_floats
    def evaluate_single(self, predicted:dict, actual:dict) -> tuple:
        """
        Calculate the accuracy of single prediction.
        Args:
            predicted (dict): Predicted stix bundle.
            actual (dict): Actual stix bundle.
        Returns:
            precision, recall, f1, res (tuple): Results of a single stix bundle prediction.
        """

        epsilon = 10**-15
        
        predicted_objects, actual_objects = self.bring_comparison_values(predicted, actual)

        # Store the results for each stix object
        res = {cti_type:deepcopy(self.results_template) for cti_type in self.cti_object_types}
        
        # Count actual object for weighted average calculations
        total_objects_length = len(actual_objects) + epsilon

        # Calculations per cti_type for single prediction
        for obj in predicted_objects:
            res[obj[0]]["pred_count"] += 1
            if obj in actual_objects:
                res[obj[0]]["true_positives"] += 1
            else:
                res[obj[0]]["false_positives"] += 1

        # Calculations per cti_type for single prediction
        for obj in actual_objects:
            res[obj[0]]["actual_count"] += 1
            if obj not in predicted_objects:
                res[obj[0]]["false_negatives"] += 1

        # Calculations per cti_type for single prediction
        for k in res.keys():
            # Check if neither predicted or actual objects exist for cti_type
            if res[k]["pred_count"]==res[k]["actual_count"]==0:
                res[k]["precision"], res[k]["recall"], res[k]["f1"] = 1, 1, 1
                res[k]["weight"] = 1
                res[k]["agg_weight"] = 1 / len(self.cti_object_types) # To be fixed
                total_objects_length += 1
            else:
                res[k]["precision"] = res[k]["true_positives"] / (res[k]["true_positives"] + res[k]["false_positives"] + epsilon)
                res[k]["recall"] = res[k]["true_positives"] / (res[k]["true_positives"] + res[k]["false_negatives"] + epsilon)
                res[k]["f1"] = 2 * res[k]["precision"] * res[k]["recall"] / (res[k]["precision"] + res[k]["recall"] + epsilon)
                res[k]["weight"] = res[k]["actual_count"]

        # Weighted average calculations for single prediction
        precision = sum([res[k]["weight"] * res[k]["precision"] / total_objects_length for k in res.keys()])
        recall = sum([res[k]["weight"] * res[k]["recall"] / total_objects_length for k in res.keys()])
        f1 = sum([res[k]["weight"] * res[k]["f1"] / total_objects_length for k in res.keys()])

        return (precision, recall, f1, res)

    @format_floats
    def evaluate(self, predicted:list, actual:list, comparison_values:list=None, cti_object_types:list=None) -> tuple:
        """
        Calculate the accuracy of multiple predictions.
        Args:
            predicted (list): List of predicted stix bundles
            actual (list): List of actual stix bundles
            comparison_values (list): List of attributes per object in stix bundle to use for evaluation
            cti_object_types (list): List of object types to use for evaluation.
        Returns:
            precision, recall, f1, res (tuple): Average results of multiple stix bundle predictions.
        """

        if len(predicted)!=len(actual):
            raise DifferentLenghtsError("Predicted objects have different length from the actual",
                                        len(predicted),
                                        len(actual))

        if comparison_values is not None:
            self.comparison_values = comparison_values
        else:
            warnings.warn("\nType and Name will be used to compare stix objects!", STIXWarning)

        if cti_object_types is not None:
            self.cti_object_types = cti_object_types
        else:
            warnings.warn("\nAll cti types will be evaluated!", STIXWarning)

        precision, recall, f1 = 0, 0, 0

        full_res = {cti_type:deepcopy(self.results_template) for cti_type in self.cti_object_types}

        total_sample = len(predicted)

        for pair in zip(predicted, actual):
            p, r, f, res = self.evaluate_single(*pair)
            precision += p / total_sample
            recall += r / total_sample
            f1 += f / total_sample
            for cti_type in full_res.keys():
                for metric in self.results_template.keys():
                    if metric.endswith("count") or metric.endswith("tives"):
                        full_res[cti_type][metric] += res[cti_type][metric]
                    else:
                        full_res[cti_type][metric] += res[cti_type]["agg_weight"] * res[cti_type][metric] / total_sample
        
        return precision, recall, f1, full_res
