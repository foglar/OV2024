import csv
import cv2 as cv
from datetime import datetime
from compare import FolderComparator
from modules import ConfigLoader
from coordinates import get_meteor_start_end_coordinates

home_dir = ConfigLoader().get_home_dir()
compare = FolderComparator()

if __name__ == "__main__":
    comparison_results = compare.find_matching_folders()    
    with open(f"{home_dir}/comparison_results.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([ "Meteor", "Date","Time","Detection Type","Location","Time","Detection Type","Location","Time Difference"])
        for result in comparison_results:
            # Convert data to the format that will be written to the CSV file

            meteor_date = datetime.strptime(result[0][2], "%d.%m.%Y")
            meteor_month = meteor_date.strftime("%m")
            meteor_time = datetime.strptime(result[0][3], "%H:%M:%S")

            if meteor_month == 10:
                meteor_month = "A"
            elif meteor_month == 11:
                meteor_month = "B"
            elif meteor_month == 12:
                meteor_month = "C"

            # TODO: how to get the meteor number? - list all meteors in the folder with date and time before meteor time
            meteor_number = "___"

            # TODO: if cannot get meteor coordinates, set detection type to "N"
            if result[0][1]:
                detection_type = "Ma"
                meteor_position = get_meteor_start_end_coordinates(result[0][0] + "/data.txt")
                # TODO: check if image exists, or find image path automatically
                meteor_img_path = result[0][0] + "/" + result[0][0].split("/")[-1] + ".jpg"
                image = cv.imread(meteor_img_path)
                height, width = image.shape[:2]
                print(meteor_position)
            else:
                detection_type = "D"
            if result[1][1]:
                detection_type1 = "Ma"
            else:
                detection_type1 = "D"

            meteor = meteor_date.strftime("%Y") + meteor_month + meteor_date.strftime("%d") + meteor_number
            date = result[0][2]
            time = result[0][3]
            location = None
            time1 = result[1][3]
            location1 = None


            string = f"{meteor},{date},{time},{detection_type},{location},{time1},{detection_type1},{location1},{result[2]}"
            print(string)