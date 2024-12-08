# CMU Interactive Data Science Final Project : Global Temperatures and Their Impact on Hurricanes and Storms

![Alt Text](EDA_Global_Temp_Data/summary.gif)
* **Team members**:
  * Gunavardhan Akiti: gakiti@andrew.cmu.edu (contact person)
  * Yashwanth Yerabudala Surendra: yashwany@andrew.cmu.edu
  * Shrey Jain: shreyj@andrew.cmu.edu
  * Kaavya Subramanian: kaavyas@andrew.cmu.edu
 
 ## Abstract
The world is getting warmer every day, and so is the debate over whether the human race should be concerned about it. In recent times, extreme weather events have affected millions. To this end, we seek to discover evidence of this phenomenon being caused by global warming, specficially looking at hurricanes and storms.We first visualize evidence by integrating two datasets that record every extreme weather event between 1980 and 2013, as well as monthly daily global temperatures. We contrast the yearly hurricane count during these years with the average land and ocean temperatures. While that doesn't yield an apparent correlation, we also visualize the path of these hurricanes on a 2D globe and view glimpses of how they get become more severe over the years. This led us to observe hurricane counts across different severity levels, which better indicate a rise in the number of category 4 and 5 hurricanes, a trend that spans multiple years. Finally, to bring it all together, we saw the effects of these events on land by tracing their path across different months and years. With this evidence, we developed a prediction model for global temperature and the expected hurricane severity at the user's input location and date. A Support Vector Regression model is used for predicting the temperature and Random Forest model is used to predict the hurricane intensity with an accuracy of 92% on held out test data.

## Streamlit App
Update.

 ## Video Link 
 Update.

## Work distribution and project process
Generally, we directly collaborated on overall plans and ideas, and split up executables to work on independently. 
- Project proposal: We all worked together to brainstorm ideas and locate datasets, and then discusssed and wrote our proposal together.
- Sketches and Data Analysis: We all discussed ideas for data analysis and visualization, and after deciding on the final outputs, we split up the data cleaning process, with two people each working on a dataset. We also each took point on a visualization to develop, which we later built into a dashboard page.
- Code development: As discussed before, we each built a separate page of the dashboard. Part of the team took point on building a predictive model for the data science project, and the others supplemented the development process in other ways. 
- Writeup and Video: We each wrote different parts of the report and the video, and collectively reviewed the final product(s).


## Running the software
1. Clone the git respository locally and navigate into the directory: `cd final-project-f24-indusinnovators`
2. Ensure the system has git-lfs installed. This is done specific to the operating sytem; for example, on a Mac with homebrew, the following command can be used :`brew install git-lfs`
3. Install git-lfs with `git lfs install` and then pull the larger files from the remote repository with `git lfs pull`
4. Run `pip install -r requirements.txt` or `python -m pip install -r requirements.txt` to import all necessary packages and versions.
5. Run the homepage file using streamlit, which provides access to all other pages: `streamlit run code/HomePage.py `

## Deliverables

### Proposal

- [x] A completed [proposal](Proposal.md). Each student should submit the URL that points to this file in their github repo on Canvas.

### Sketches

- [X] Develop sketches/prototype of your project.

Note: The copy of the repo is made public to allow deployment using streamlit cloud. Repo link: https://github.com/YashwanthYS/final-project-f24-indusinnovators-deployment

### Final deliverables

- [ ] All code for the project should be in the repo.
- [ ] Update the **Online URL** above to point to your deployed project.
- [ ] A detailed [project report](Report.md).  Each student should submit the URL that points to this file in their github repo on Canvas.
- [ ] A 5 minute video demonstration.  Upload the video to this github repo and link to it from your report.
