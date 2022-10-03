import matplotlib.pyplot as plt

def plot_muli_lines(x:list, Ys:list, labels=None):

    if labels == None:
        labels = range(len(Ys))

    for index, y in enumerate(Ys):
        plt.plot(x, y, label = labels[index])
    plt.legend()
    plt.show()