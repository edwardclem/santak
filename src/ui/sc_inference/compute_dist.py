import cv2
import multiprocessing as mp

def create_batches(contours, num_batches=4):
    '''
    Takes a dictionary of contours and produces list of batches of tuples
    TODO: handle leftover batch
    '''

    batches = []
    cnt_list = list(contours.items())

    batch_len = int(len(cnt_list)/num_batches)

    for i in range(num_batches):
        if i + 1 < num_batches:
            batches.append(cnt_list[batch_len*i:batch_len*(i + 1)])
        else:
            batches.append(cnt_list[batch_len*i:])

    return batches

def process_batch(target, batch, outq):
    '''
    Processes a batch of shapes, puts the results in the output queue.
    '''

    #create new shape context extractor

    sc_extractor = cv2.createShapeContextDistanceExtractor()

    for char_id, contour  in batch:
        dist = sc_extractor.computeDistance(target, contour)
        outq.put((char_id, dist))

    print("finished batch processing")

if __name__=="__main__":
    test_dict = dict((i, 2*i) for i in range(30))

    batches = create_batches(test_dict, 4)
    for batch in batches:
        print(batch)
