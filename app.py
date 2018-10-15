import dash
import dash_core_components as dcc
import dash_html_components as html

import numpy as np
import pandas as pd

import savor
import FD_scrape



df2, ingred_list, main_list, bool_vec, sales_vec, \
           recipe_mat,recipe_mat_norm, orig_prices     = savor.initialize()


global recipe_title, recipe_ingredients, recipe_directions, \
sale_ingredients, other_ingredients, sale_prices, \
sale_titles, savings_amounts, savings_percent, \
orig_cost, sale_cost


# scrape sales pages
auto_scrape = False  # turn scraping ON (True) or OFF (False)

if auto_scrape:
    # - only scrape sales if they haven't already been checked within the last 24 hrs
    FD_scrape.scrape_sales()



def generate_output():
    if auto_scrape:
      # - only scrape sales if they haven't already been checked within the last 24 hrs
      FD_scrape.scrape_sales()

    return html.Div([
        html.Div(dcc.Dropdown(
        id='dropdown',
        options=[
            {'label': '1. '  + recipe_title[0] + ' ---- $' + sale_cost[0] + 
                                                 ' (was $' + orig_cost[0] + ')'  +
                                                 ' -- SAVE ' + savings_percent[0] + '%', 
                'value': 0},
            {'label': '2. '  + recipe_title[1] + ' ---- $' + sale_cost[1] + 
                                                 ' (was $' + orig_cost[1] + ')'  +
                                                 ' -- SAVE ' + savings_percent[1] + '%', 
                'value': 1},
            {'label': '3. '  + recipe_title[2] + ' ---- $' + sale_cost[2] + 
                                                 ' (was $' + orig_cost[2] + ')'  +
                                                 ' -- SAVE ' + savings_percent[2] + '%', 
                'value': 2},
            {'label': '4. '  + recipe_title[3] + ' ---- $' + sale_cost[3] + 
                                                 ' (was $' + orig_cost[3] + ')'  +
                                                 ' -- SAVE ' + savings_percent[3] + '%', 
                'value': 3},
            {'label': '5. '  + recipe_title[4] + ' ---- $' + sale_cost[4] + 
                                                 ' (was $' + orig_cost[4] + ')'  +
                                                 ' -- SAVE ' + savings_percent[4] + '%', 
                'value': 4},
            {'label': '6. '  + recipe_title[5] + ' ---- $' + sale_cost[5] + 
                                                 ' (was $' + orig_cost[5] + ')'  +
                                                 ' -- SAVE ' + savings_percent[5] + '%', 
                'value': 5},
            {'label': '7. '  + recipe_title[6] + ' ---- $' + sale_cost[6] + 
                                                 ' (was $' + orig_cost[6] + ')'  +
                                                 ' -- SAVE ' + savings_percent[6] + '%', 
                'value': 6},
            {'label': '8. '  + recipe_title[7] + ' ---- $' + sale_cost[7] + 
                                                 ' (was $' + orig_cost[7] + ')'  +
                                                 ' -- SAVE ' + savings_percent[7] + '%', 
                'value': 7},
            {'label': '9. '  + recipe_title[8] + ' ---- $' + sale_cost[8] + 
                                                 ' (was $' + orig_cost[8] + ')'  +
                                                 ' -- SAVE ' + savings_percent[8] + '%', 
                'value': 8},
            {'label': '10. ' + recipe_title[9] + ' ---- $' + sale_cost[9] + 
                                                 ' (was $' + orig_cost[9] + ')'  +
                                                 ' -- SAVE ' + savings_percent[9] + '%', 
                'value': 9},
        ],
        value=0,
        clearable=False,
        ), style={'width':'50%','padding':10,'font-size':'115%',}),

    ])

    

app = dash.Dash()
app.title = 'supersavor'

server = app.server  # the underlying Flask app

app.config['suppress_callback_exceptions']=True

app.layout = html.Div([

    html.Div([
        html.Span("super",style={'color':'#01b7c4'}),
        html.Span(html.U("savor"),style={'color':'#f7a013'}),   
    ], style={'font-size':'500%', 
              'font-family':'verdana',
              'text-align':'center',
              'padding':25
             }
    ),

    html.Div([html.I('Save time and money by finding recipes that optimizes online savings.')
        ], style={'font-size':'100%', 
              'font-family':'verdana',
              'text-align':'center',
              'padding':15,
              'marginBottom':25
             }
        ),


    html.Div([ 
        # html.Div('Online Grocer', style={'font-family':'verdana',
        #                                  'font-size':'150%',
        #                                  'text-align':'center'}),
        # html.Div(dcc.Dropdown(
        #     options=[
        #         {'label': 'FreshDirect', 'value': 'FD'}
        #     ],
        #     value='FD'
        # ), style={'width':'90%', 'padding':25,
        #           'font-family':'verdana'
        #           }
        # ),

        html.Div('Recipe Preferences', style={'font-family':'verdana',
                                              'font-size':'150%',
                                              'text-align':'center',
                                                }),
        html.Div(dcc.Checklist(
            id='checkboxes',
            options=[
                {'label': 'Fruits', 'value': 'F'},
                {'label': 'Vegetables', 'value': 'V'},
                {'label': 'Poultry', 'value': 'P'},
                {'label': 'Meat', 'value': 'M'},
                {'label': 'Seafood', 'value': 'S'}
            ],
            values=['F', 'V', 'P', 'M', 'S']
        ), style={'width': '90%', 'padding':25
                 }
        ),

        html.Div('Budget', style={'font-family':'verdana',
                                  'font-size':'150%',
                                  'text-align':'center'}),
        html.Div(dcc.RangeSlider(
            id='slider',
            min=0,
            max=50,
            step=5,
            #marks={i: '$'+ str(i) for i in range(10, 60, 10)},
            marks={10: '$10', 20: '$20', 30: '$30', 40: '$40', 50: '$50+'},
            value=[5,25],
        ), style={'width': '90%', 'padding':25
                 }
        ),
    ], style={'columnCount': 2}
    ),

    #html.Label('Text Input'),
    #dcc.Input(value='MTL', type='text'),


    # button
    html.Div(
        html.Button(html.B('Find Sales and Recipes'), 
            id='button', n_clicks=0,
            style={'font-family':'verdana',
                   'font-size':'150%',
                   'color':'white',
                   'background-color': '#617693',
                   }
        ), style={'padding':40,
                  'text-align':'center'
                 }
    ),

    html.Div([
    html.Div(dcc.Dropdown(
        id='dropdown',
        options=[
            {'label': ' ', 'value': 0},
        ],
        value=0
        ), style={'width':'0%','height':0,'display':'none'}  # <-- HIDE
        ),   
            # we need to create this layout element, otherwise
            # it can't find "dropdown" in the callback below.  But,
            # we need to create this "dropdown" every time button is
            # pushed since the labels change.  So current solution, is
            # to create this in layout and just hide it.
    ],
    ),

    html.Div(id='table-container', #id='output-container-button',
            children='', 
            style={'width':'200%'}),
    
    
        

    # button output table
    #html.Div(id='table-container'),

    # Tabs

    dcc.Tabs(id="tabs-example", value='tab-1-example', 
        children=[
        dcc.Tab(label='Ingredients', value='tab-1-example',
                style={'font-family':'verdana',
                       'background-color':'#01b7c4'}
                ),
        dcc.Tab(label='Directions',  value='tab-2-example',
                style={'font-family':'verdana',
                       'background-color':'#f7a013'}
                ),

    ], style={'font-family':'verdana',

             }
    ),

    html.Div(id='tabs-content',
             style={'font-family':'verdana',
                   }
            ),



    html.Div([html.I('Note: grocery sales are found on FreshDirect.com. Recipe cost estimates are based on servings for two.')
        ], style={'font-size':'50%', 
              'font-family':'verdana',
              'text-align':'center',
              'padding':10,
              'marginTop':50
             }
        ),
    


    # button output table
    #html.Div(id='output-test'),

    #

    

], style={'padding-left':'15%',
          'width': '70%',}  #, style={'columnCount': 2})
)



@app.callback(
    dash.dependencies.Output('table-container', 'children'),
    [dash.dependencies.Input('button', 'n_clicks')],
    [dash.dependencies.State('checkboxes','values'), 
     dash.dependencies.State('slider','value')])
def update_output(n_clicks,checkbox_values,slider_values):
    #print(checkbox_values)

    global recipe_title, recipe_ingredients, recipe_directions, \
    sale_ingredients, other_ingredients, sale_prices, \
    sale_titles, savings_amounts, savings_percent, \
    orig_cost, sale_cost

    if n_clicks>0:

        recipe_title, recipe_ingredients, recipe_directions, \
        sale_ingredients, other_ingredients, sale_prices, \
        sale_titles, savings_amounts, savings_percent, \
        orig_cost, sale_cost = savor.update( \
        df2, ingred_list, main_list, bool_vec, sales_vec, \
        recipe_mat,recipe_mat_norm, orig_prices, \
        checkbox_values, slider_values) 

        #return generate_output(checkbox_values,slider_values)
        return generate_output()
    return


@app.callback(
    dash.dependencies.Output('tabs-content', 'children'),
    [dash.dependencies.Input('tabs-example', 'value'),
     dash.dependencies.Input('button', 'n_clicks_'),
     dash.dependencies.Input('dropdown', 'value'),
    ],
    [dash.dependencies.State('dropdown','value'),
     dash.dependencies.State('button','n_clicks'),
    ])

def render_content(tab,n_clicks_,drop_value_,drop_value,n_clicks):
    global recipe_title, recipe_ingredients, recipe_directions, \
    sale_ingredients, other_ingredients, sale_prices, \
    sale_titles, savings_amounts, savings_percent, \
    orig_cost, sale_cost

    j = drop_value
    #print('dropdown value: ' + str(j))

    if n_clicks>0:
        if tab == 'tab-1-example':
            return html.Div([
                #html.P('recipe ingredients'),
                html.Table(
                    [html.Tr(recipe_ingredients[j][i]) for i in range(len(recipe_ingredients[j]))]
                    ),
                #html.P('sale ingredients'),
                #html.Table(
                #    [html.Tr(sale_ingredients[j][i]) for i in range(len(sale_ingredients[j]))]
                #    ),
                html.P(html.I('Items for sale online')),
                html.Table(
                    [html.Tr(sale_titles[j][i]) for i in range(len(sale_titles[j]))]
                    ),     
            ])
        elif tab == 'tab-2-example':
            return html.Div([
                html.Table(
                    [html.Tr( str(i+1)+ '. ' + recipe_directions[j][i]) for i in range(len(recipe_directions[j]))]
                ),
            ])



if __name__ == '__main__':
    #app.run_server(debug=True)
    app.run_server(debug=False, host='0.0.0.0', port=8050)
