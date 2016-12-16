# coding: utf-8
#__original_author__ =  'Humberto Brandão'
#__tweak__ = 'Team Monami'
import pandas as pd
import xgboost as xgb

# from matplotlib import pylab as plt
# import operator

# Load data and roughly clean it, then sort as game date
df = pd.read_csv("data.csv")
df.drop(['game_event_id', 'game_id', 'lat', 'lon', 'team_id', 'team_name'], axis=1, inplace=True)
df.sort_values('game_date',  inplace=True)
mask = df['shot_made_flag'].isnull()

# Clean data
actiontypes = dict(df.action_type.value_counts())
df['type'] = df.apply(lambda row: row['action_type'] if actiontypes[row['action_type']] > 25 else 'others', axis=1)
df.drop(['action_type', 'combined_shot_type'], axis=1, inplace=True)

df['away'] = df.matchup.str.contains('@')
df.drop('matchup', axis=1, inplace=True)

df['distance'] = df.apply(lambda row: row['shot_distance'] if row['shot_distance'] <45 else 45, axis=1)
df['time_remaining'] = df.apply(lambda row: row['minutes_remaining'] * 60 + row['seconds_remaining'], axis=1)
df['last_moments'] = df.apply(lambda row: 1 if row['time_remaining'] < 3 else 0, axis=1)

data = pd.get_dummies(df['type'],prefix="action_type")

features=["away", "period", "playoffs", "shot_type", "shot_zone_area", "shot_zone_basic", "season",
           "shot_zone_range", "opponent", "last_moments"]
for f in features:
    data = pd.concat([data, pd.get_dummies(df[f], prefix=f),], axis=1)
data = pd.concat([data, df['distance'],], axis=1)

data.rename(columns=lambda x: x.replace(" ",""),inplace=True)
X = data[~mask]
y = df.shot_made_flag[~mask]

dtrain=xgb.DMatrix(data=X, label=y, missing =None)

param ={        'objective'           : "binary:logistic",
                'booster'             : "gbtree",
                'eval_metric'         : "logloss",
                'eta'                 : 0.012,
                'max_depth'           : 10,
                'subsample'           : 0.82,
                'colsample_bytree'    : 0.60,
                'seed'                : 1,
                'silent'              : 1
}
clf = xgb.cv(   params                 = param,
                dtrain                 = dtrain,
                num_boost_round        = 1000,
                maximize               = False,
                nfold                  = 5,
                early_stopping_rounds  = 20
);
clf[[0]].min(0)

bestround = clf[[0]].idxmin(0)

bst = xgb.train(    params              = param,
                    dtrain              = dtrain,
                    num_boost_round     = bestround,
                    verbose_eval        = 1,
                    maximize            = False
)

target_x = data[mask]
target_id = df[mask]["shot_id"]
dtest =xgb.DMatrix(data=target_x, missing =None)
preds = bst.predict(dtest)
submission = pd.DataFrame({"shot_id": target_id, "shot_made_flag": preds})
submission = submission.sort_values('shot_id')
submission.to_csv("submit_xgboost_ref.csv", index=False)


# def ceate_feature_map(features):
    # outfile = open('xgb.fmap', 'w')
    # i = 0
    # for feat in features:
        # outfile.write('{0}\t{1}\tq\n'.format(i, feat))
        # i = i + 1
    # outfile.close()

# ceate_feature_map(list(X.columns))
# # ceate_feature_map(features)
# importance = bst.get_fscore(fmap='xgb.fmap')
# importance = sorted(importance.items(), key=operator.itemgetter(1))

# df = pd.DataFrame(importance, columns=['feature', 'fscore'])
# df['fscore'] = df['fscore'] / df['fscore'].sum()

# plt.figure()
# df.plot()
# df.plot(kind='barh', x='feature', y='fscore', legend=False, figsize=(25, 30))
# plt.title('XGBoost Feature Importance')
# plt.xlabel('relative importance')
# plt.gcf().savefig('feature_importance_xgb.png')
