import cv2
import numpy as np

impath1 = 'render_chars/rendered/73728.png'

impath2 = 'render_chars/rendered/73729.png'

img1 = cv2.imread(impath1)
img2 = cv2.imread(impath2)

edges1 = cv2.Canny(img1,300,300)
edges2 = cv2.Canny(img2,300,300)

#now find contours?

_, contours1, _ = cv2.findContours(edges1, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
_, contours2, _ = cv2.findContours(edges2, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

cv2.drawContours(img1, contours1, -1, (0,255,0), 3)
cv2.drawContours(img2, contours2, -1, (0,255,0), 3)

#flatten contour arrays
#causes weird drawing but need to merge to compare shape context
all_contours1 = np.concatenate(contours1)
all_contours2 = np.concatenate(contours2)

#TODO: subsampling contour points

sc = cv2.createShapeContextDistanceExtractor()

print(sc.computeDistance(all_contours1, all_contours1))

# cv2.drawContours(img1, all_contours1, -1, (0,255,0), 3)
# cv2.drawContours(img2, all_contours2, -1,(0,255,0), 3)

cv2.imshow("73728 - contours", img1)
cv2.imshow("73729 - contours", img2)
cv2.waitKey(0)
cv2.destroyAllWindows()
