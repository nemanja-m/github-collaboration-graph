import os
import csv
import glob
import argparse
import pandas as pd


def save_nodes(nodes, filename, node_id, label):
    with open(filename, 'w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(['{}:ID'.format(node_id), ':LABEL'])

        for node in nodes:
            writer.writerow([node, label])

    print('* {} nodes saved to \'{}\''.format(label, filename))


def save_edges(relationships, filename, type):
    with open(filename, 'w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow([':START_ID', ':END_ID', ':TYPE'])

        for user, repo in relationships:
            writer.writerow([user, repo, type])

    print('* {} edges saved to \'{}\''.format(type, filename))


def get_graph_data(filename):
    df = pd.read_csv(filename, usecols=['user', 'repo_name'])
    df.drop_duplicates(inplace=True)

    users = df['user'].tolist()
    repos = df['repo_name'].tolist()
    memberships = []
    ownerships = []

    for _, user, repo_name in df.itertuples():
        if repo_name[0] == '/':
            raise RuntimeError(
                'In {} file: repo_name starts with /'.format(filename)
            )

        memberships.append((user, repo_name))
        owner, _ = repo_name.split('/')
        users.append(owner)
        ownerships.append((owner, repo_name))

    return users, repos, memberships, ownerships


def main(args):
    csv_files = glob.glob(args.input + '/*.csv')

    print('\n=> {} files found'.format(len(csv_files)))

    if len(csv_files) == 0:
        exit(0)

    print('=> Processing ...\n')

    user_nodes = set()
    repo_nodes = set()
    membership_edges = set()
    ownership_edges = set()

    for filename in csv_files:
        print('* {}'.format(os.path.basename(filename)))

        users, repos, memberships, ownerships = get_graph_data(filename)

        user_nodes.update(users)
        repo_nodes.update(repos)
        membership_edges.update(memberships)
        ownership_edges.update(ownerships)

    print('\n{:12} {}'.format('Users:', len(user_nodes)))
    print('{:12} {}'.format('Repos:', len(repo_nodes)))
    print('{:12} {}'.format('Memberships:', len(membership_edges)))
    print('{:12} {}'.format('Ownerships:', len(ownership_edges)))

    print('\n=> Saving nodes and relationships to CSV files ...\n')

    users_path = os.path.join(args.output, 'users.csv')
    repos_path = os.path.join(args.output, 'repos.csv')
    memberships_path = os.path.join(args.output, 'memberships.csv')
    ownerships_path = os.path.join(args.output, 'ownerships.csv')

    save_nodes(user_nodes, users_path, 'username', 'User')
    save_nodes(repo_nodes, repos_path, 'repo_name', 'Repo')
    save_edges(membership_edges, memberships_path, 'MEMBER')
    save_edges(ownership_edges, ownerships_path, 'OWNER')

    print('\n=> Done!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Creates graph nodes and relationships from CSV files'
    )
    parser.add_argument('--input', type=str, default='./')
    parser.add_argument('--output', type=str, default='./')
    args = parser.parse_args()

    main(args)
