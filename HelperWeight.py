# Define a function to convert SBMI to pounds
def sbmi_to_pounds(sbmi, height, age, gender):
    # Convert height from inches to meters
    height_m = height * 0.0254
    # Rearrange the SBMI formula to get BMI
    bmi = (sbmi + 5.4 + 10.8 * gender - 0.23 * age) / 1.2
    # Calculate weight in kilograms using the BMI formula
    weight_kg = bmi * height_m ** 2
    # Convert weight from kilograms to pounds
    weight_lbs = weight_kg * 2.20462
    # Return weight in pounds
    return weight_lbs

# Define a function to calculate the possible weight range using SBMI
def calculatePossibleWeightRange(gender, age, height):
    # Create an empty dictionary to store the results
    result = {}
    # Define the SBMI categories and ranges according to [SBMI calculator]
    categories = ["underweight", "normal", "overweight", "obese", "clinically_obese"]
    ranges = [[0, 20], [20, 25], [25, 30], [30, 40], [40, float("inf")]]
    # Loop through each category and range
    for category, range in zip(categories, ranges):
        # Calculate the lower and upper bounds of weight in pounds for each range using the sbmi_to_pounds function
        lower_bound = sbmi_to_pounds(range[0], height, age, gender)
        upper_bound = sbmi_to_pounds(range[1], height, age, gender)
        # Store the results in the dictionary with the category as the key and the bounds as the value
        result[category] = [lower_bound, upper_bound]
    # Return the result dictionary
    return result

# Example usage
#gender = 1 # 1 for male and 0 for female
#age = 30 # in years
#height = 70 # in inches

#print(calculatePossibleWeightRange(gender, age, height))