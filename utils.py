from rightcolumn.display_plot_images import display_plots


class Data:
    def __init__(self,main_frame):
        self.results_lists = []
        self.filter_runs = {}
        self.smoothing_factor = 1
        self.membrane_area = 1
        self.headers = []
        self.analysis_number = 0
        self.project_title = "Project"
        self.initiate_analysis_number()
        self.stats_item = None
        self.images_item = None
        self.images = []
        self.first_batch_of_images = False
        self.second_batch_of_images = False
        self.main_frame = main_frame
        self.rightColumn = None
        self.leftColumn = None
        self.tk = None
        self.images_container = None
        self.current_image_index = 0
        self.image_label = None

    def set_image_label(self, image_label):
        self.image_label = image_label

    def get_image_label(self):
        return self.image_label

    def setRightColumn(self, rightColumn):
        self.rightColumn = rightColumn

    def setLeftColumn(self, leftColumn):
        self.leftColumn = leftColumn

    def setTk(self, tk):
        self.tk = tk

    def setImagesContainer(self, images_container):
        self.images_container = images_container

    def set_stats_item(self, stats_item):
        self.stats_item = stats_item

    def set_images_item(self, images_item):
        self.images_item = images_item

    def enable_first_batch_of_images(self):
        self.first_batch_of_images = True
        self.images = ["flux.png", "flux_vs_load.png", "J_vs_load.png", "loading.png"]
        # display_plot_images(self.rightColumn, self.tk, self)

    def enable_last_batch_of_images(self):
        self.second_batch_of_images = True
        self.images = ["plot_label.png", "flux_mode_JJ0_Load(Lm²).png", "flux_mode_JJ0_Time(min).png",
                       "flux_mode_JJ0_Volume(mL).png", "flux_mode_Load(Lm²).png",
                       "flux_mode_Time(min).png", "flux_mode_Volume(mL).png",
                       "flux.png", "flux_vs_load.png", "J_vs_load.png", "loading.png"]
        # display_plot_images(self.rightColumn, self.tk, self)

    def get_images(self):
        return self.images

    def get_current_image_index(self):
        return self.current_image_index

    def set_current_image_index(self, index):
        self.current_image_index = index

    def set_results(self, results_lists):
        self.results_lists = results_lists
        return self.results_lists

    def set_filter_runs(self, filter_runs):
        self.filter_runs = filter_runs
        return self.filter_runs

    def set_smoothing_factor(self, smoothing_factor):
        self.smoothing_factor = smoothing_factor
        return self.smoothing_factor

    def set_membrane_area(self, membrane_area):
        self.membrane_area = membrane_area
        return self.membrane_area

    def get_results_lists(self):
        return self.results_lists

    def get_filter_runs(self):
        return self.filter_runs

    def get_smoothing_factor(self):
        return self.smoothing_factor

    def get_membrane_area(self):
        return self.membrane_area

    def initiate_analysis_number(self):
        file = open("last_analysis.txt", "r")
        last_project_number = file.readline()
        last_project_number = int(last_project_number.strip())
        file.close()
        last_project_number += 1
        self.analysis_number = last_project_number
        self.project_title = "Analysis_" + str(last_project_number)

    def write_the_project_directory(self):
        file = open("last_analysis.txt", "w")
        file.write(str(self.analysis_number))
        file.close()

    def get_project_title(self):
        return self.project_title

    def update_stat_items(self, new_text):
        self.stats_item.delete("1.0", "end")  # Clear the existing text
        self.stats_item.insert("1.0", new_text)  # Insert the new text
