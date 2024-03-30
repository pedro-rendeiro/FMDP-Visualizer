""" MDP-Explore

This is a tool for graphically illustrating the (possibly time-dependent)
Markov chain underlying a Markov Decision Process (MDP).
"""

import graphviz as gv
import wx

# Define the MDP in mdp.py
from mdp import *

class MDPExplore(wx.Frame):
    """ MDP-Explore application """

    def __init__(self, parent, title):
        super(MDPExplore, self).__init__(parent, title=title,size=(400, 300))

        # Generate an initial plot of the MDP
        self.hasUI = False
        self.plotMDPGraph(self.generateMDPGraph(0, 0, state_labels()))

        self.initUI()
        self.hasUI = True

        self.Centre()
        self.Show()

    def initUI(self):
        """ Build the UI """
        self.panel = wx.Panel(self)

        # Components
        self.mdp_image = wx.StaticBitmap(self.panel, wx.ID_ANY, wx.Bitmap('./img/mdp.png', wx.BITMAP_TYPE_ANY))

        self.sc_time = wx.SpinCtrl(self.panel, value='0')
        self.sc_time.SetRange(0, 10000)

        controls = [str(x) for x in range(0, number_of_controls())]
        self.cob_control = wx.ComboBox(self.panel, value='0', choices=controls, style=wx.CB_READONLY)

        self.chb_probs = wx.CheckBox(self.panel, label='Show probabilities')
        self.chb_probs.SetValue(True)

        self.chb_state_numbers = wx.CheckBox(self.panel, label='Show state numbers')
        self.chb_state_numbers.SetValue(False)

        self.chb_use_percentage = wx.CheckBox(self.panel, label='Use %')
        self.chb_use_percentage.SetValue(False)

        self.chb_save_pdf = wx.CheckBox(self.panel, label='Save to pdf')
        self.chb_save_pdf.SetValue(False)

        # Bind events
        self.sc_time.Bind(wx.EVT_SPINCTRL, self.updateMDPPlot)
        self.cob_control.Bind(wx.EVT_COMBOBOX, self.updateMDPPlot)
        self.chb_probs.Bind(wx.EVT_CHECKBOX, self.updateMDPPlot)
        self.chb_state_numbers.Bind(wx.EVT_CHECKBOX, self.updateMDPPlot)
        self.chb_save_pdf.Bind(wx.EVT_CHECKBOX, self.updateMDPPlot)
        self.chb_use_percentage.Bind(wx.EVT_CHECKBOX, self.updateMDPPlot)

        # Sizers
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)

        vboxl = wx.BoxSizer(wx.VERTICAL)
        vboxr = wx.BoxSizer(wx.VERTICAL)

        # Create the layout
        vboxl.Add(self.mdp_image, 1, wx.EXPAND|wx.ALL, 5)

        vboxr.Add(wx.StaticText(self.panel, label='Time:'))
        vboxr.Add(self.sc_time, 0, wx.ALL, 5)

        vboxr.Add(wx.StaticText(self.panel, label='Control:'))
        vboxr.Add(self.cob_control, 0, wx.ALL, 5)

        vboxr.Add(self.chb_probs, 0, wx.TOP, 10)
        vboxr.Add(self.chb_state_numbers, 0, wx.TOP, 10)
        vboxr.Add(self.chb_use_percentage, 0, wx.TOP, 10)
        vboxr.Add(self.chb_save_pdf, 0, wx.TOP, 10)

        self.hbox.Add(vboxl, 1, wx.EXPAND|wx.TOP|wx.BOTTOM|wx.LEFT, 5)
        self.hbox.Add(vboxr, 0, wx.ALL, 5)

        self.panel.SetSizer(self.hbox)
        self.hbox.Fit(self)
        self.panel.Layout()

    def generateMDPGraph(self, u, k, labels):
        """ Construct the (graphviz) graph of the MDP """
        line_width = 5.0
        mdp = gv.Digraph(format='png')
        # Set layout engine (see other options in graphviz/docs/layouts)
        mdp.engine = 'sfdp'
        
        if u > number_of_controls():
            print("ERROR: %i is not a valid control action!" % u)
            u = 0
        
        if u == 0:
            action = 'Take a regular shot'
        elif u == 1:
            action = 'Take a blind shot'

        for i in range(0, number_of_states()):
            # State nodes
            if i in labels:
                # Whether or not to show state numbers in state nodes
                if not self.hasUI or not self.chb_state_numbers.GetValue():
                    mdp.node(str(i), labels[i], style='filled', fillcolor='lightblue')
                else:
                    mdp.node(str(i), str(i) + ':' + labels[i], style='filled', fillcolor='lightblue')
            else:
                mdp.node(str(i), 'Node %i' % i)
            
            # Action nodes
            mdp.node(str(i) + str(u), action, shape='box')
            # Edges from state to action nodes
            mdp.edge(str(i), str(i) + str(u), style='dashed')            

        # Create edges
        for i in range(0, number_of_states()):
            psum = 0.0
            for j in range(0, number_of_states()):
                p = TProb(i, j, k, u)

                if TProb(i, j, k, u) > 0:
                    if not self.hasUI:
                        mdp.edge(str(i) + str(u), str(j), '%.2f' % p, {'penwidth':str(line_width * p)})
                    else:
                        # Whether or not to show probabilities
                        if self.chb_probs.GetValue():
                            # Whether or not to show probabilities using percentage values
                            if self.chb_use_percentage.GetValue():
                                mdp.edge(str(i) + str(u), str(j), '%.1f%%' % (100.0 * p), {'penwidth':str(line_width * p)})
                            else:
                                mdp.edge(str(i) + str(u), str(j), '%.2f' % p, {'penwidth':str(line_width * p)})
                        else:
                            mdp.edge(str(i) + str(u), str(j), None, {'penwidth':str(line_width * p)})

                    psum += p

            if abs(psum - 1.0) > 1e-6:
                print ("WARNING: The transition matrix has a row (%i) that does not sum to one!" % i)
                print ("         It sums to %f." % psum)

        return mdp

    def plotMDPGraph(self, mdp):
        """ Render graphviz graph of the MDP to file """
        mdp.render(filename='img/mdp', cleanup=True)

        if self.hasUI and self.chb_save_pdf.GetValue():
            mdp.format = 'pdf'
            mdp.render(filename='img/mdp', cleanup=True)
            mdp.format = 'png'

    def updateMDPPlot(self, e):
        """ Update the plot of the MDP
        
        This saves the graphviz graph of the MDP to file and updates the UI
        container.
        """
        self.plotMDPGraph(self.generateMDPGraph(int(self.cob_control.GetValue()), self.sc_time.GetValue(), state_labels()))
        self.mdp_image.SetBitmap(wx.Bitmap('./img/mdp.png', wx.BITMAP_TYPE_ANY))
        self.hbox.Fit(self)

def main():
    """ Run the application """
    app = wx.App()
    MDPExplore(None, title='MDP-Explore 0.3')
    app.MainLoop()

if __name__ == '__main__':
    main()

