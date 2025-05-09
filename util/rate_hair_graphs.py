from img_util import rate_hair
import pandas as pd
import os
import cv2
import numpy as np
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt

"""Helper python script to find optimal parameters for the rate_hair function.
will plot and save the results in the """



data_path = "../data/annotated_hair"


# save ratios

# set up directories and files
folder_path = "../data/hair_annotations"
ah = pd.read_csv("../data/annotations.csv")
ah.drop(columns= ['Hair_Ratio'], inplace= True)

def ratioedB(row):

    # get filepath, open image in RGB format
    filename = row['FileID'] + '.png'
    filepath = os.path.join(folder_path, filename)
    img = cv2.imread(filepath)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # compute ratio
    ratio ,_,_ = rate_hair(img_rgb)
    
    return ratio

ah['Hair_Ratio'] = ah.apply(ratioedB, axis= 1)
ah.to_csv("../data/annotations.csv", index= False)


# save ratios (no blur)

# set up directories and files
folder_path = "../data/hair_annotations"
ah = pd.read_csv("../data/annotations.csv")
ah.drop(columns= ['Hair_Ratio_noB'], inplace= True)

def ratioed(row):

    #get filepath, open image in RGB format
    filename = row['FileID'] + '.png'
    filepath = os.path.join(folder_path, filename)
    img = cv2.imread(filepath)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # compute ratio
    ratio ,_,_ = rate_hair(img_rgb, blur= False)
    
    return ratio

ah['Hair_Ratio_noB'] = ah.apply(ratioed, axis= 1)
ah.to_csv("../data/annotations.csv", index= False)


# compute optimal thresholds

ah = pd.read_csv("../data/annotations.csv")

# get information from the train set
train_set = ah[ah['Group_ID'] != 'C']
true_labels = train_set['Rating_Final']
ratios = train_set['Hair_Ratio']

# initialize variables to store best results
best_acc = 0
best_t1, best_t2 = None, None

# list to save values to plot later
acc_lB = []
t1_lB = []
t2_lB = []

# iterate through possible threshold values
for t1 in np.linspace(0.0, 1.0, 100):
    for t2 in np.linspace(t1 + 0.01, 1.0, 100):

        t1_lB.append(t1)
        t2_lB.append(t2)

        predicted_labels = np.array([0 if r < t1 else 1 if r < t2 else 2 for r in ratios])

        acc = accuracy_score(true_labels, predicted_labels)
        acc_lB.append(acc)
        
        if acc > best_acc:
            best_acc = acc
            best_t1, best_t2 = t1, t2

print(f"WITH BLUR | Best thresholds: t1 = {best_t1:.3f}, t2 = {best_t2:.3f}; with accuracy = {best_acc:.4f}")


# compute optimal thresholds (no blur)

# get information from the train set
train_set = ah[ah['Group_ID'] != 'C']
true_labels = train_set['Rating_Final']
ratios = train_set['Hair_Ratio_noB']

# initialize variables to store best results
best_acc = 0
best_t1, best_t2 = None, None

# list to save values to plot later
acc_l = []
t1_l = []
t2_l = []

# iterate through possible threshold values
for t1 in np.linspace(0.0, 1.0, 100):
    for t2 in np.linspace(t1 + 0.01, 1.0, 100):

        t1_l.append(t1)
        t2_l.append(t2)

        predicted_labels = np.array([0 if r < t1 else 1 if r < t2 else 2 for r in ratios])

        acc = accuracy_score(true_labels, predicted_labels)
        acc_l.append(acc)
        
        if acc > best_acc:
            best_acc = acc
            best_t1, best_t2 = t1, t2

print(f"  NO BLUR | Best thresholds: t1 = {best_t1:.3f}, t2 = {best_t2:.3f}; with accuracy = {best_acc:.4f}")


# plot results

fig = plt.figure(figsize=(12, 5))

# plot for normal images
ax1 = fig.add_subplot(1, 2, 1, projection='3d')
ax1.scatter(t1_l, t2_l, acc_l, c= acc_l, cmap= 'viridis', alpha= 0.6)

ax1.view_init(elev=30, azim=135)

ax1.set_title("Accuracy score\n(without image blur)")
ax1.set_xlabel('Lower threshold')
ax1.set_ylabel('Upper threshold')
ax1.set_zlabel('Accuracy')

# plot for blurred images
ax2 = fig.add_subplot(1, 2, 2, projection='3d')
ax2.scatter(t1_lB, t2_lB, acc_lB, c= acc_lB, cmap= 'viridis', alpha= 0.6)

ax2.view_init(elev=30, azim=135)

ax2.set_title("Accuracy score\n(with image blur)")
ax2.set_xlabel('Lower threshold')
ax2.set_ylabel('Upper threshold')
ax2.set_zlabel('Accuracy')

plt.tight_layout()
plt.savefig("../data/3D_accuracy_thresholds.png", dpi=300)
plt.close()
print("Plot saved as [3D_accuracy_thresholds.png] in the /data directory.")

# compute optimal parameter

folder_path = "../data/hair_annotations"

ah = pd.read_csv("../data/annotations.csv")

# get information from the train set
train_set = ah[ah['Group_ID'] != 'C']
true_labels = train_set['Rating_Final']

# initialize variables to store best results
best_acc = 0
best_accB = 0
best_param = 0
best_paramB = 0

# list to save values to plot later
acc_l = []
acc_lB = []
param_l = []

# iterate over parameter values
for p in range(0,255, 5):

    # list to store predictions (no blur and blur)
    pred_labels = []
    pred_labelsB = []
    param_l.append(p)

    # predict labels
    for i, row in train_set.iterrows():

        # load image
        filename = row['FileID'] + '.png'
        img_path = os.path.join(folder_path, filename)
        img = cv2.imread(img_path)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # compute label with and without blur
        _, label, _ = rate_hair(img_rgb, t1= 0.061, t2= 0.268, dst= p, blur= False)
        _, labelB, _ = rate_hair(img, dst= p)
        pred_labels.append(label)
        pred_labelsB.append(labelB)

    # compute accuracy score with and without blur
    acc = accuracy_score(true_labels, pred_labels)
    accB = accuracy_score(true_labels, pred_labelsB)
    acc_l.append(acc)
    acc_lB.append(accB)

    # update best results appropriately
    if acc > best_acc:
        best_acc = acc
        best_param = p
    
    if accB > best_accB:
        best_accB = accB
        best_paramB = p

print(f"  NO BLUR | Best parameter: {best_param}; with accuracy: {best_acc:.4f} ")
print(f"WITH BLUR | Best parameter: {best_paramB}; with accuracy: {best_accB:.4f} ()")


# plot results

plt.plot(param_l, acc_l, label='Without Blur', marker='o')
plt.plot(param_l, acc_lB, label='With Blur', marker='o')
plt.xlabel("Parameter value")
plt.ylabel("Accuracy")
plt.title("Accuracy Comparison: Blurred vs. Not Blurred Image")
plt.grid(True)
plt.legend()
plt.savefig("../data/2D_accuracy_parameter.png", dpi=300)
plt.close()
print("Plot saved as [2D_accuracy_parameter.png] in the /data directory.")


# accuracy on original annotations

test_set = ah[ah['Group_ID'] == 'C']

true_labels = test_set['Rating_Final']
ratios = test_set['Hair_Ratio']
predicted_labels = np.array([0 if r < 0.020 else 1 if r < 0.118 else 2 for r in ratios])
print(f"Accuracy on test data (annotations from group C mandatory assigment: {accuracy_score(true_labels, predicted_labels):.4f}")